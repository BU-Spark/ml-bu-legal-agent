import re
import base64
from pathlib import Path
from typing import List, Dict, Tuple

import chainlit as cl
from chainlit.input_widget import Select
from pypdf import PdfReader
from openai import OpenAI

from config import load_api_key, SCRAPED_VECTOR_DB_DIR, LEGAL_TACTICS_SCRAPED_DB_DIR
from vector_store import load_vector_store, query_vector_store


# Backend initialization (same core RAG pipeline)
load_api_key(".env")
VECTOR_DB = load_vector_store(LEGAL_TACTICS_SCRAPED_DB_DIR)
SCRAPED_VECTOR_DB = load_vector_store(SCRAPED_VECTOR_DB_DIR)

DEFAULT_ROLE = "general"
ALLOWED_ROLES = {"general", "tenant", "landlord"}
MIN_TEXT_CHARS_FOR_NON_OCR = 250
MAX_OCR_PAGES = 12


def _history_to_context(messages: List[Dict[str, str]], max_turns: int = 3) -> str:
    if not messages:
        return ""
    turns = messages[-(max_turns * 2):]
    lines = []
    for msg in turns:
        role = msg.get("role", "").strip().lower()
        content = str(msg.get("content", "")).strip()
        if not content:
            continue
        if role == "assistant":
            content = re.split(r"\n\n---\n\n###", content)[0].strip()
            lines.append(f"Assistant: {content}")
        elif role == "user":
            lines.append(f"User: {content}")
    return "\n".join(lines).strip()


def _token_set(text: str) -> set:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9']+", (text or "").lower()))


def _chunk_text(text: str, chunk_size: int = 1100, overlap: int = 180) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks


def _extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")
    return "\n".join(pages_text).strip()


def _ocr_pdf_with_openai(pdf_path: str, max_pages: int = MAX_OCR_PAGES) -> Tuple[str, str]:
    """
    OCR scanned/image PDF pages using OpenAI Vision via rendered page images.
    Returns (text, status_message). status_message is empty on success.
    """
    try:
        import pypdfium2 as pdfium
    except Exception:
        return "", "Missing dependency `pypdfium2` for rendering PDF pages."

    try:
        client = OpenAI()
    except Exception as exc:
        return "", f"OpenAI client init failed: {exc}"

    try:
        doc = pdfium.PdfDocument(pdf_path)
        page_count = min(len(doc), max_pages)
        extracted_pages = []

        for i in range(page_count):
            page = doc[i]
            pil_image = page.render(scale=2.0).to_pil()

            from io import BytesIO
            buf = BytesIO()
            pil_image.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            data_url = f"data:image/png;base64,{b64}"

            resp = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "Extract all readable text from this document page exactly as written. "
                                    "Return plain text only. Preserve key line breaks."
                                ),
                            },
                            {"type": "input_image", "image_url": data_url},
                        ],
                    }
                ],
            )
            page_text = (resp.output_text or "").strip()
            if page_text:
                extracted_pages.append(page_text)

        return "\n\n".join(extracted_pages).strip(), ""
    except Exception as exc:
        return "", f"OpenAI OCR fallback failed: {exc}"


def _ingest_pdf_session_doc(pdf_path: str, display_name: str) -> Tuple[Dict, str]:
    extracted = _extract_text_from_pdf(pdf_path)
    status_note = ""

    # If regular extraction is weak, use OpenAI OCR fallback for scanned PDFs.
    if len(extracted) < MIN_TEXT_CHARS_FOR_NON_OCR:
        ocr_text, ocr_status = _ocr_pdf_with_openai(pdf_path)
        if len(ocr_text) > len(extracted):
            extracted = ocr_text
            status_note = "Used OpenAI OCR fallback (scanned/image PDF support)."
        elif ocr_status:
            status_note = ocr_status

    chunks = _chunk_text(extracted, chunk_size=1100, overlap=180)
    doc = {
        "name": display_name,
        "text": extracted,
        "chunks": chunks,
    }
    return doc, status_note


def _retrieve_relevant_doc_context(query: str, docs: List[Dict], top_k: int = 3) -> str:
    if not docs:
        return ""

    q = _token_set(query)
    scored = []
    for doc in docs:
        for chunk in doc.get("chunks", []):
            s = _token_set(chunk)
            if not s:
                continue
            # Simple overlap score tuned for legal text relevance.
            score = len(q & s) / max(1, len(q))
            if score > 0:
                scored.append((score, doc["name"], chunk))

    if not scored:
        return ""

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]
    blocks = []
    for _, name, chunk in top:
        blocks.append(f"[From uploaded PDF: {name}]\n{chunk}")
    return "\n\n".join(blocks)


def _extract_pdf_paths_from_message(message: cl.Message) -> List[Tuple[str, str]]:
    """
    Returns list of (path, display_name) for uploaded PDFs found in the message.
    """
    found = []
    elements = getattr(message, "elements", []) or []
    for element in elements:
        mime = str(getattr(element, "mime", "") or "")
        path = str(getattr(element, "path", "") or "")
        name = str(getattr(element, "name", "") or Path(path).name or "uploaded.pdf")
        if mime == "application/pdf" and path:
            found.append((path, name))
    return found


def _normalize_conversational_response(text: str) -> str:
    if not text:
        return ""
    banned_headers = {"your question", "answer", "key takeaways", "action items"}
    cleaned = []
    for raw in str(text).splitlines():
        line = raw.rstrip()
        normalized = line.strip()
        key = re.sub(r"^[#>\-\*\s]+", "", normalized)
        key = re.sub(r":\s*$", "", key).strip().lower()
        if key in banned_headers:
            continue
        line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
        cleaned.append(line)
    text = "\n".join(cleaned)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def _format_answer(response: str, citations: List[str]) -> str:
    if citations:
        citation_text = "\n\n".join(citations)
        return f"{response}\n\n---\n\n### Sources\n\n{citation_text}"
    return response


def _extract_followups(raw_response: str, user_query: str, role: str, max_items: int = 3) -> List[str]:
    candidates = []
    candidates.extend(re.findall(r'[“"]([^“”"\n]{8,220}\?)["”]', raw_response or ""))
    for line in (raw_response or "").splitlines():
        line = line.strip(" -*•\t")
        if line.endswith("?") and 12 <= len(line) <= 220:
            candidates.append(line)

    fallbacks = {
        "tenant": [
            "What rights do tenants have?",
            "Can my landlord increase rent?",
            "What should I do if repairs are ignored?",
        ],
        "landlord": [
            "What notices are required before filing eviction?",
            "How should I document communication with a tenant?",
            "What legal risks should I avoid first?",
        ],
        "general": [
            "What rights do tenants have?",
            "Can my landlord increase rent?",
            "What should I do if repairs are ignored?",
        ],
    }

    if not candidates:
        candidates.extend(fallbacks.get(role, fallbacks["general"]))

    unique = []
    seen = set()
    for item in candidates + fallbacks.get(role, fallbacks["general"]):
        clean = re.sub(r"\s+", " ", item).strip()
        key = clean.lower()
        if key in seen or len(clean) < 12 or len(clean) > 220:
            continue
        if clean.lower() == user_query.strip().lower():
            continue
        seen.add(key)
        unique.append(clean)
        if len(unique) >= max_items:
            break
    return unique[:max_items]


def _build_followup_actions(suggestions: List[str]) -> List[cl.Action]:
    actions = []
    for i, suggestion in enumerate(suggestions):
        if not suggestion:
            continue
        actions.append(
            cl.Action(
                name=f"followup_{i}",
                label=f"💬 {suggestion}",
                payload={"question": suggestion},
            )
        )
    return actions


def _build_role_actions() -> List[cl.Action]:
    return [
        cl.Action(name="role_general", label="General", payload={"role": "general"}),
        cl.Action(name="role_tenant", label="Tenant", payload={"role": "tenant"}),
        cl.Action(name="role_landlord", label="Landlord", payload={"role": "landlord"}),
    ]


async def _answer_query(user_text: str):
    text = (user_text or "").strip()
    if not text:
        return

    role = cl.user_session.get("role", DEFAULT_ROLE)
    history = cl.user_session.get("history", [])
    uploaded_docs = cl.user_session.get("uploaded_docs", [])

    # Slash command to switch persona quickly.
    if text.lower().startswith("/role "):
        requested = text.split(" ", 1)[1].strip().lower()
        if requested in ALLOWED_ROLES:
            cl.user_session.set("role", requested)
            await cl.Message(content=f"Role updated to `{requested}`.").send()
        else:
            await cl.Message(content="Invalid role. Use `/role general`, `/role tenant`, or `/role landlord`.").send()
        return

    if not VECTOR_DB or not SCRAPED_VECTOR_DB:
        await cl.Message(content="Error: Vector store not loaded. Please verify backend setup.").send()
        return

    thinking = cl.Message(content="Thinking...")
    await thinking.send()

    short_context = _history_to_context(history, max_turns=3)
    uploaded_context = _retrieve_relevant_doc_context(text, uploaded_docs, top_k=3)
    contextual_query = text
    context_parts = []
    if short_context:
        context_parts.append(f"Conversation so far:\n{short_context}")
    if uploaded_context:
        context_parts.append(
            "Relevant excerpts from user's uploaded PDF(s):\n"
            f"{uploaded_context}"
        )
    if context_parts:
        contextual_query = "\n\n".join(context_parts) + f"\n\nCurrent user question: {text}"

    response, citations = query_vector_store(
        SCRAPED_VECTOR_DB,
        VECTOR_DB,
        contextual_query,
        role=role,
    )
    cleaned = _normalize_conversational_response((response or "").strip())
    answer = _format_answer(cleaned, citations)

    history.extend(
        [
            {"role": "user", "content": text},
            {"role": "assistant", "content": answer},
        ]
    )
    cl.user_session.set("history", history)

    suggestions = _extract_followups(cleaned, text, role, max_items=3)
    actions = _build_followup_actions(suggestions)

    thinking.content = answer
    thinking.actions = []
    await thinking.update()
    if actions:
        await cl.Message(content="Suggested questions:", actions=actions).send()


async def _set_role(role: str):
    requested = (role or "").strip().lower()
    if requested not in ALLOWED_ROLES:
        await cl.Message(content="Invalid role. Use general, tenant, or landlord.").send()
        return
    cl.user_session.set("role", requested)
    await cl.Message(content=f"Role updated to `{requested}`.").send()


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    cl.user_session.set("role", DEFAULT_ROLE)
    cl.user_session.set("uploaded_docs", [])

    await cl.ChatSettings(
        [
            Select(
                id="role",
                label="Mode",
                values=["general", "tenant", "landlord"],
                initial_value=DEFAULT_ROLE,
            )
        ]
    ).send()

    starters = [
        "What rights do tenants have?",
        "Can my landlord increase rent?",
        "What should I do if repairs are ignored?",
    ]
    actions = _build_followup_actions(starters)
    role_actions = _build_role_actions()
    await cl.Message(
        content=(
            "### ★ Star — Massachusetts Housing Law Assistant\n"
            "Ask a question to start.\n\n"
            "You can also upload a PDF (e.g., rent agreement). "
            "The document is processed for this chat session only."
        ),
        actions=role_actions,
    ).send()
    await cl.Message(content="Suggested questions:", actions=actions).send()


@cl.on_settings_update
async def on_settings_update(settings):
    role = (settings or {}).get("role", DEFAULT_ROLE)
    await _set_role(role)


@cl.on_message
async def on_message(message: cl.Message):
    pdfs = _extract_pdf_paths_from_message(message)
    if pdfs:
        current_docs = cl.user_session.get("uploaded_docs", [])
        for path, name in pdfs:
            doc, status = _ingest_pdf_session_doc(path, name)
            if not doc.get("chunks"):
                await cl.Message(
                    content=(
                        f"Uploaded `{name}`, but I could not extract usable text. "
                        f"{status or 'Please try a clearer PDF.'}"
                    )
                ).send()
                continue
            current_docs.append(doc)
            status_suffix = f" {status}" if status else ""
            await cl.Message(
                content=(
                    f"Loaded `{name}` for this session "
                    f"({len(doc['chunks'])} chunks).{status_suffix}"
                )
            ).send()
        cl.user_session.set("uploaded_docs", current_docs)

    # If user only uploaded file with empty text message, avoid sending empty query.
    if not (message.content or "").strip():
        return

    await _answer_query(message.content)


@cl.action_callback("followup_0")
@cl.action_callback("followup_1")
@cl.action_callback("followup_2")
async def on_followup(action: cl.Action):
    question = (action.payload or {}).get("question", "").strip()
    if question:
        await _answer_query(question)


@cl.action_callback("role_general")
@cl.action_callback("role_tenant")
@cl.action_callback("role_landlord")
async def on_role_action(action: cl.Action):
    role = (action.payload or {}).get("role", "").strip()
    if role:
        await _set_role(role)
