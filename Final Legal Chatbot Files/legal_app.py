import re
import gradio as gr

from config import load_api_key, SCRAPED_VECTOR_DB_DIR, LEGAL_TACTICS_SCRAPED_DB_DIR
from vector_store import load_vector_store, query_vector_store


APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=Public+Sans:wght@400;500;600&display=swap');

:root {
  --bg-main: linear-gradient(170deg, #fbfbfb 0%, #f2f2f2 100%);
  --bg-radial-1: radial-gradient(860px 460px at -10% -8%, rgba(242, 242, 242, 0.92) 0%, rgba(242, 242, 242, 0) 62%);
  --bg-radial-2: radial-gradient(880px 460px at 115% -15%, rgba(224, 224, 224, 0.72) 0%, rgba(224, 224, 224, 0) 60%);
  --ink: #171717;
  --muted: #4f4f4f;
  --panel: rgba(255, 255, 255, 0.94);
  --panel-border: #dcdcdc;
  --topbar-border: #e8e8e8;
  --chat-bg: linear-gradient(180deg, #ffffff 0%, #f8f8f8 100%);
  --chat-border: #dddddd;
  --assistant-bubble: #ffffff;
  --assistant-border: #e3e3e3;
  --user-bubble: #f3f1ef;
  --input-bg: #ffffff;
  --input-border: #d7d7d7;
  --chip: #f2f2f2;
  --chip-border: #d8d8d8;
  --accent: #cf4520;
  --accent-2: #a83314;
  --accent-soft: #f6e3dd;
  --shadow: 0 22px 56px rgba(0, 0, 0, 0.14);
}

.dark, [data-theme="dark"] {
  --bg-main: linear-gradient(170deg, #0f0f0f 0%, #1a1a1a 100%);
  --bg-radial-1: radial-gradient(860px 460px at -10% -8%, rgba(70, 70, 70, 0.35) 0%, rgba(70, 70, 70, 0) 62%);
  --bg-radial-2: radial-gradient(880px 460px at 115% -15%, rgba(55, 55, 55, 0.32) 0%, rgba(55, 55, 55, 0) 60%);
  --ink: #f2f2f2;
  --muted: #b2b2b2;
  --panel: rgba(25, 25, 25, 0.92);
  --panel-border: #414141;
  --topbar-border: #3a3a3a;
  --chat-bg: linear-gradient(180deg, #141414 0%, #101010 100%);
  --chat-border: #3f3f3f;
  --assistant-bubble: #1d1d1d;
  --assistant-border: #404040;
  --user-bubble: #302821;
  --input-bg: #1e1e1e;
  --input-border: #4a4a4a;
  --chip: #262626;
  --chip-border: #4a4a4a;
  --accent: #ff7a52;
  --accent-2: #ff9a7b;
  --accent-soft: #4b3128;
  --shadow: 0 24px 64px rgba(0, 0, 0, 0.42);
}

html, body, .gradio-container {
  min-height: 100%;
  background: var(--bg-radial-1), var(--bg-radial-2), var(--bg-main) !important;
}

.gradio-container, .gradio-container .main, .gradio-container .wrap {
  background: transparent !important;
  color: var(--ink);
  font-family: "Public Sans", sans-serif;
}

.gradio-container {
  --body-background-fill: transparent !important;
  --body-text-color: var(--ink) !important;
  --color-accent: var(--accent) !important;
  --block-background-fill: transparent !important;
  --block-border-color: var(--panel-border) !important;
  --input-background-fill: var(--input-bg) !important;
  --input-border-color: var(--input-border) !important;
}

.gradio-container, .gradio-container * {
  color: var(--ink);
}

#app-title, #app-title h1, #app-subtitle, #app-subtitle p {
  color: var(--ink) !important;
}

.gradio-container a {
  color: var(--accent);
}

#shell {
  max-width: 1100px;
  margin: 0 auto;
  padding: 18px 14px 14px;
}

#app-title h1 {
  font-family: "Manrope", sans-serif;
  letter-spacing: 0.1px;
  margin-bottom: 4px;
  font-weight: 800;
  font-size: 1.95rem;
}

#app-title .brand-star {
  color: var(--accent) !important;
}

#app-subtitle p {
  color: var(--muted);
  margin-top: 0;
  margin-bottom: 10px;
}

#app-shell {
  background: var(--panel) !important;
  border: 1px solid var(--panel-border) !important;
  border-radius: 22px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
  padding: 14px;
}

#topbar {
  align-items: end !important;
  gap: 10px !important;
  border-bottom: 1px solid var(--topbar-border);
  margin-bottom: 12px;
  padding-bottom: 10px;
}

#chat-window {
  border: 1px solid var(--chat-border) !important;
  border-radius: 16px;
  background: var(--chat-bg);
  min-height: 60vh;
}

#chat-window .message-row {
  animation: fade-in 0.2s ease;
}

#chat-window .message {
  border-radius: 14px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

#chat-window .message.user {
  background: var(--user-bubble) !important;
}

#chat-window .message.bot,
#chat-window .message.assistant {
  background: var(--assistant-bubble) !important;
  border: 1px solid var(--assistant-border);
}

#composer textarea {
  border-radius: 12px !important;
  border: 1px solid var(--input-border) !important;
  background: var(--input-bg) !important;
  min-height: 70px;
}

#composer label,
#role-select label {
  font-weight: 600 !important;
}

#send-btn button {
  border-radius: 12px !important;
  font-weight: 700;
  border: 1px solid var(--accent-2) !important;
  background: linear-gradient(180deg, var(--accent) 0%, var(--accent-2) 100%) !important;
}

#send-btn button:hover {
  filter: brightness(1.05);
}

#rec-title p {
  color: var(--muted);
  margin: 10px 0 6px;
  font-size: 0.94rem;
}

#clear-btn button {
  border-radius: 10px !important;
  border: 1px solid var(--chip-border) !important;
  background: var(--chip) !important;
}

#rec-row button {
  border-radius: 999px !important;
  border: 1px solid var(--chip-border) !important;
  background: var(--chip) !important;
  font-size: 0.84rem !important;
  line-height: 1.2 !important;
}

#rec-row button:hover {
  border-color: var(--accent-2) !important;
  background: var(--accent-soft) !important;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(3px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 980px) {
  #shell {
    padding: 8px 6px;
  }
  #app-shell {
    padding: 10px;
  }
  #chat-window {
    min-height: 54vh;
  }
  #topbar {
    gap: 8px !important;
  }
}

@media (max-width: 720px) {
  #app-title h1 {
    font-size: 1.35rem;
  }
  #topbar {
    flex-direction: column !important;
    align-items: stretch !important;
  }
  #composer-row {
    flex-direction: column !important;
    gap: 8px !important;
  }
  #send-btn {
    width: 100% !important;
  }
  #chat-window {
    min-height: 50vh;
  }
}
"""


# Load API key and vector stores on startup
load_api_key(".env")
vector_db = load_vector_store(LEGAL_TACTICS_SCRAPED_DB_DIR)
scraped_vector_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)


def make_links_clickable(text):
    """Convert Markdown links [text](url) to HTML anchors that open in a new tab."""
    return re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2" target="_blank">\1</a>', text)


def _history_to_context(chat_history, max_turns=3):
    """Build compact multi-turn context so follow-up questions keep state."""
    if not chat_history:
        return ""
    turns = chat_history[-(max_turns * 2):]
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


def _format_response(response, citations, role):
    role_label = f"> **Answering as:** {role.capitalize()}\n\n"
    answer = make_links_clickable(response)
    if citations:
        citation_text = "\n\n".join(make_links_clickable(c) for c in citations)
        return f"{role_label}{answer}\n\n---\n\n### Sources\n\n{citation_text}"
    return f"{role_label}{answer}"


def _extract_followups(raw_response, user_query, role, max_items=3):
    candidates = []
    candidates.extend(re.findall(r'[“"]([^“”"\n]{8,220}\?)["”]', raw_response or ""))
    for line in (raw_response or "").splitlines():
        line = line.strip(" -*•\t")
        if line.endswith("?") and 12 <= len(line) <= 220:
            candidates.append(line)

    fallbacks = {
        "tenant": [
            "What documents should I collect before taking the next step?",
            "If my landlord ignores this, what legal options do I have next?",
            "Can you outline a step-by-step action plan for this week?",
        ],
        "landlord": [
            "What notices and documentation are legally required in Massachusetts?",
            "How should I communicate this to avoid procedural mistakes?",
            "What is the safest next step before filing anything in court?",
        ],
        "general": [
            "Can you summarize this in a simple step-by-step checklist?",
            "What deadlines or timelines should I watch out for?",
            "What evidence should I keep to support my case?",
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

    while len(unique) < max_items:
        unique.append("")
    return unique[:max_items]


def _recommendation_payload(suggestions):
    button_updates = []
    state_values = []
    for suggestion in suggestions:
        if suggestion:
            button_updates.append(gr.update(value=suggestion, visible=True))
            state_values.append(suggestion)
        else:
            button_updates.append(gr.update(value="", visible=False))
            state_values.append("")
    return (*button_updates, *state_values)


def chat_with_star(user_query, chat_history, role):
    if chat_history is None:
        chat_history = []

    text = (user_query or "").strip()
    if not text:
        empty_updates = _recommendation_payload(["", "", ""])
        return chat_history, "", *empty_updates, chat_history

    if not vector_db or not scraped_vector_db:
        error_message = "Error: Vector store not loaded. Please ensure the backend is set up correctly."
        chat_history = chat_history + [
            {"role": "user", "content": text},
            {"role": "assistant", "content": error_message},
        ]
        rec_updates = _recommendation_payload([
            "How do I fix missing vector store files?",
            "Which setup script should I run first?",
            "Can you verify my environment checklist?",
        ])
        return chat_history, "", *rec_updates, chat_history

    short_context = _history_to_context(chat_history, max_turns=3)
    contextual_query = text
    if short_context:
        contextual_query = (
            "Conversation so far:\n"
            f"{short_context}\n\n"
            f"Current user question: {text}"
        )

    response, citations = query_vector_store(
        scraped_vector_db,
        vector_db,
        contextual_query,
        role=role,
    )
    answer_text = (response or "").strip()
    formatted_response = _format_response(answer_text, citations, role)
    chat_history = chat_history + [
        {"role": "user", "content": text},
        {"role": "assistant", "content": formatted_response},
    ]

    suggestions = _extract_followups(answer_text, text, role, max_items=3)
    rec_updates = _recommendation_payload(suggestions)
    return chat_history, "", *rec_updates, chat_history


def clear_chat():
    hidden = gr.update(value="", visible=False)
    return [], "", hidden, hidden, hidden, "", "", "", []


if __name__ == "__main__":
    with gr.Blocks(title="★ Star - Massachusetts Housing Law Assistant", css=APP_CSS) as iface:
        with gr.Column(elem_id="shell"):
            gr.Markdown(
                "<h1><span class='brand-star'>★</span> Star | Massachusetts Housing Law Assistant</h1>",
                elem_id="app-title",
            )
            gr.Markdown(
                "A conversation-first legal assistant with citations to Massachusetts housing sources.",
                elem_id="app-subtitle",
            )

            with gr.Column(elem_id="app-shell"):
                with gr.Row(elem_id="topbar"):
                    gr.Markdown(
                        "**Conversation**  \nAsk follow-ups naturally. Citations remain attached to answers."
                    )
                    role_input = gr.Dropdown(
                        choices=["general", "tenant", "landlord"],
                        label="Perspective",
                        value="general",
                        elem_id="role-select",
                        scale=1,
                    )
                    clear_btn = gr.Button("Clear Chat", elem_id="clear-btn", scale=0)

                chatbot = gr.Chatbot(
                    label="Chat",
                    height=620,
                    sanitize_html=False,
                    elem_id="chat-window",
                    layout="bubble",
                )
                chat_state = gr.State([])

                gr.Markdown("Suggested next questions", elem_id="rec-title")
                with gr.Row(elem_id="rec-row"):
                    rec_btn1 = gr.Button(visible=False)
                    rec_btn2 = gr.Button(visible=False)
                    rec_btn3 = gr.Button(visible=False)
                rec_state1 = gr.State("")
                rec_state2 = gr.State("")
                rec_state3 = gr.State("")

                with gr.Row(elem_id="composer-row"):
                    query_input = gr.Textbox(
                        label="Message",
                        placeholder="Ask your question here...",
                        lines=2,
                        scale=6,
                        elem_id="composer",
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1, elem_id="send-btn")

        submit_outputs = [
            chatbot,
            query_input,
            rec_btn1,
            rec_btn2,
            rec_btn3,
            rec_state1,
            rec_state2,
            rec_state3,
            chat_state,
        ]

        submit_btn.click(
            fn=chat_with_star,
            inputs=[query_input, chat_state, role_input],
            outputs=submit_outputs,
        )
        query_input.submit(
            fn=chat_with_star,
            inputs=[query_input, chat_state, role_input],
            outputs=submit_outputs,
        )

        rec_btn1.click(
            fn=chat_with_star,
            inputs=[rec_state1, chat_state, role_input],
            outputs=submit_outputs,
        )
        rec_btn2.click(
            fn=chat_with_star,
            inputs=[rec_state2, chat_state, role_input],
            outputs=submit_outputs,
        )
        rec_btn3.click(
            fn=chat_with_star,
            inputs=[rec_state3, chat_state, role_input],
            outputs=submit_outputs,
        )

        clear_btn.click(
            fn=clear_chat,
            inputs=[],
            outputs=submit_outputs,
        )

    iface.launch(server_name="0.0.0.0")
