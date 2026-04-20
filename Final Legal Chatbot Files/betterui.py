import re
import streamlit as st

from config import load_api_key, SCRAPED_VECTOR_DB_DIR, LEGAL_TACTICS_SCRAPED_DB_DIR
from vector_store import load_vector_store, query_vector_store


PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=Public+Sans:wght@400;500;600&display=swap');

:root {
  --bg-main: #0f1115;
  --bg-soft: #141821;
  --surface-1: rgba(20, 24, 31, 0.88);
  --surface-2: rgba(17, 21, 29, 0.72);
  --line: #2a323f;
  --line-soft: #232a35;
  --text: #edf1f7;
  --muted: #9ea8b7;
  --accent: #d08a67;
  --accent-strong: #bc7755;
  --shadow: 0 18px 46px rgba(0, 0, 0, 0.32);
}

.stApp {
  background:
    radial-gradient(980px 520px at -5% -14%, rgba(61, 79, 110, 0.26) 0%, rgba(61, 79, 110, 0) 62%),
    radial-gradient(860px 480px at 110% -20%, rgba(66, 55, 48, 0.24) 0%, rgba(66, 55, 48, 0) 60%),
    linear-gradient(170deg, #0d1015 0%, #12161d 100%);
  color: var(--text);
  font-family: "Public Sans", sans-serif;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu,
footer {
  display: none !important;
}

.block-container {
  max-width: 900px;
  padding-top: 0.2rem;
  padding-bottom: 0.08rem;
}

.app-frame {
  background: var(--surface-1);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(10px);
  padding: 0.56rem 0.6rem 0.36rem;
}

.topbar {
  border-bottom: 1px solid var(--line-soft);
  margin-bottom: 0.34rem;
  padding-bottom: 0.3rem;
}

.brand-title {
  font-family: "Manrope", sans-serif;
  font-weight: 800;
  letter-spacing: 0.1px;
  font-size: 1.42rem;
  color: var(--text);
  margin-bottom: 0.02rem;
  line-height: 1.15;
}

.brand-title .star {
  color: var(--accent);
}

.sub {
  color: var(--muted);
  margin-bottom: 0;
  font-size: 0.84rem;
  line-height: 1.35;
}

.chat-shell {
  border: 1px solid var(--line-soft);
  background: var(--surface-2);
  border-radius: 16px;
  padding: 0.56rem;
  min-height: 62vh;
}

.empty-state {
  border: none;
  border-radius: 0;
  padding: 0.3rem 0.1rem 0.2rem;
  background: transparent;
  margin-bottom: 0.34rem;
}

.empty-title {
  font-family: "Manrope", sans-serif;
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.18rem;
  color: var(--text);
}

.empty-sub {
  color: var(--muted);
  font-size: 0.86rem;
  margin-bottom: 0;
}

.msg-wrap {
  display: flex;
  width: 100%;
  margin: 0.34rem 0;
}

.msg-wrap.user {
  justify-content: flex-end;
}

.msg-wrap.assistant {
  justify-content: flex-start;
}

.msg-bubble {
  max-width: 86%;
  border-radius: 16px;
  border: 1px solid #2f3744;
  padding: 0.46rem 0.68rem;
}

.msg-bubble.user {
  background: #2a313d;
}

.msg-bubble.assistant {
  background: #181d26;
}

.sources-card {
  margin-top: 0.38rem;
  border: 1px solid #344154;
  background: rgba(28, 35, 47, 0.62);
  border-radius: 10px;
  padding: 0.4rem 0.52rem 0.34rem;
}

.sources-title {
  font-size: 0.72rem;
  letter-spacing: 0.02em;
  color: #bcc8da;
  margin-bottom: 0.2rem;
}

.rec-heading {
  color: var(--muted);
  margin: 0.2rem 0 0.2rem;
  font-size: 0.8rem;
}

div.stButton > button,
[data-testid="stBaseButton-secondary"] {
  border-radius: 999px;
  border: 1px solid #364252;
  background: #1f2835;
  color: var(--text);
  min-height: 1.9rem;
  padding: 0 0.9rem;
  font-size: 0.79rem;
  font-weight: 500;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
  transition: background-color 160ms ease, border-color 160ms ease, box-shadow 160ms ease, transform 120ms ease;
}

div.stButton > button:hover {
  border-color: var(--accent);
  background: #232d3a;
  box-shadow: 0 0 0 3px rgba(208, 138, 103, 0.12);
}

[data-testid="stSelectbox"] label {
  display: none !important;
}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  border-radius: 999px !important;
  border: 1px solid #364252 !important;
  background: #1f2835 !important;
  min-height: 1.9rem;
  padding-left: 0.45rem !important;
  padding-right: 0.4rem !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
  transition: border-color 160ms ease, box-shadow 160ms ease;
}

[data-testid="stSelectbox"] div[data-baseweb="select"] * {
  color: var(--text) !important;
  font-size: 0.79rem !important;
}

[data-testid="stSelectbox"] svg {
  width: 16px !important;
  height: 16px !important;
  color: var(--muted) !important;
}

/* Composer: fixed premium input surface */
[data-testid="stBottomBlockContainer"] {
  background: transparent !important;
  padding-top: 0 !important;
}

[data-testid="stChatInput"] {
  border-top: none !important;
  background: transparent !important;
  padding-top: 0.06rem !important;
}

[data-testid="stChatInput"] > div {
  background: rgba(19, 24, 33, 0.95) !important;
  border: 1px solid #344052 !important;
  border-radius: 16px !important;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  padding: 0.14rem 0.28rem !important;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}

[data-testid="stChatInput"] textarea {
  background: transparent !important;
  border: none !important;
  color: #f7f9fd !important;
  caret-color: #f7f9fd !important;
  font-size: 0.94rem !important;
  padding-top: 0.26rem !important;
  padding-bottom: 0.18rem !important;
}

[data-testid="stChatInput"] input,
[data-testid="stChatInput"] [contenteditable="true"] {
  color: #f7f9fd !important;
  caret-color: #f7f9fd !important;
}

[data-testid="stChatInput"] textarea::placeholder {
  color: #8c97a8 !important;
  opacity: 1 !important;
}

[data-testid="stChatInput"] input::placeholder,
[data-testid="stChatInput"] [contenteditable="true"]::placeholder {
  color: #8c97a8 !important;
  opacity: 1 !important;
}

[data-testid="stChatInput"] button {
  border-radius: 10px !important;
  border: 1px solid #42516a !important;
  background: #223047 !important;
  color: #eaf0f9 !important;
  min-height: 1.9rem !important;
  transition: background-color 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}

[data-testid="stChatInput"] button:hover {
  border-color: var(--accent) !important;
  color: #ffffff !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  color: var(--text);
  line-height: 1.48;
  margin-bottom: 0.34rem;
}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
[data-testid="stChatInput"] > div:focus-within {
  border-color: #4f6079 !important;
  box-shadow: 0 0 0 2px rgba(127, 146, 176, 0.16) !important;
}

a {
  color: #d7b095 !important;
}

@media (max-width: 820px) {
  .brand-title {
    font-size: 1.28rem;
  }
  .msg-bubble {
    max-width: 92%;
  }
  .chat-shell {
    min-height: 54vh;
  }
  .topbar [data-testid="stHorizontalBlock"] {
    flex-direction: column !important;
    gap: 0.42rem !important;
  }
  .topbar [data-testid="column"] {
    width: 100% !important;
    flex: 1 1 100% !important;
  }
}
</style>
"""

LIGHT_OVERRIDES = """
<style>
:root {
  --surface-1: rgba(255, 255, 255, 0.93);
  --surface-2: rgba(250, 250, 252, 0.82);
  --line: #dde2ea;
  --line-soft: #e7ebf1;
  --text: #1b212d;
  --muted: #687487;
  --accent: #af6947;
  --accent-strong: #955638;
  --shadow: 0 16px 40px rgba(24, 31, 44, 0.12);
}

.stApp {
  background:
    radial-gradient(980px 520px at -5% -14%, rgba(220, 226, 236, 0.34) 0%, rgba(220, 226, 236, 0) 62%),
    radial-gradient(860px 480px at 110% -20%, rgba(233, 224, 216, 0.26) 0%, rgba(233, 224, 216, 0) 60%),
    #f6f7f9;
}

.app-frame {
  background: #ffffff;
  border: 1px solid #d9e0ea;
  box-shadow: 0 10px 24px rgba(29, 45, 67, 0.08);
}

.topbar {
  border-bottom: 1px solid var(--line-soft);
}

.chat-shell {
  border: 1px solid #dde4ef;
  background: #f5f8fc;
}

.empty-state {
  border: none;
  background: transparent;
}

.empty-sub {
  color: #5f6f84;
}

div.stButton > button {
  border: 1px solid #cfd8e4;
  background: #eef3f9;
  color: var(--text);
}

div.stButton > button:hover {
  border: 1px solid var(--accent) !important;
  background: #faf2ee !important;
  color: #1f2530 !important;
  box-shadow: 0 0 0 3px rgba(175, 105, 71, 0.14);
}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  border: 1px solid #cfd8e4 !important;
  background: #edf3fa !important;
}

.msg-bubble {
  border: 1px solid #d4dde9;
}

.msg-bubble.user {
  background: #e8eef7;
}

.msg-bubble.assistant {
  background: #ffffff;
}

.sources-card {
  border: 1px solid #ced9e7;
  background: #eef4fb;
}

.sources-title {
  color: #5f6f84;
}

[data-testid="stChatInput"] {
  background: transparent !important;
}

[data-testid="stChatInput"] > div {
  background: #ffffff !important;
  border: 1px solid #cfd8e5 !important;
  box-shadow: 0 8px 18px rgba(29, 45, 67, 0.11);
}

[data-testid="stChatInput"] textarea {
  color: #1b2432 !important;
  caret-color: #1b2432 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
  color: #8a95a6 !important;
  opacity: 1 !important;
}

[data-testid="stChatInput"] input,
[data-testid="stChatInput"] [contenteditable="true"] {
  color: #1b2432 !important;
  caret-color: #1b2432 !important;
}

[data-testid="stChatInput"] input::placeholder,
[data-testid="stChatInput"] [contenteditable="true"]::placeholder {
  color: #8a95a6 !important;
  opacity: 1 !important;
}

[data-testid="stChatInput"] button {
  background: #f4f7fb !important;
  border: 1px solid #cfd8e6 !important;
  color: #1f2530 !important;
}

[data-testid="stChatInput"] button:hover {
  border: 1px solid var(--accent) !important;
  background: #faf2ee !important;
}

[data-testid="stChatInput"] > div:focus-within {
  border-color: #aeb9ca !important;
  box-shadow: 0 0 0 2px rgba(159, 173, 194, 0.22) !important;
}

a {
  color: #9a5f41 !important;
}
</style>
"""


def _history_to_context(messages, max_turns=3):
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


def _format_answer(response, citations, role):
    if citations:
        citation_text = "\n\n".join(citations)
        return f"{response}\n\n---\n\n### Sources\n\n{citation_text}"
    return f"{response}"


def _normalize_conversational_response(text):
    """Remove section-style formatting so answers read like natural chat messages."""
    if not text:
        return ""

    banned_headers = {"your question", "answer", "key takeaways", "action items"}
    cleaned_lines = []

    for raw_line in str(text).splitlines():
        line = raw_line.rstrip()
        normalized = line.strip()

        # Drop section labels like "### Key Takeaways" or "Answer:"
        key = re.sub(r"^[#>\-\*\s]+", "", normalized)
        key = re.sub(r":\s*$", "", key).strip().lower()
        if key in banned_headers:
            continue

        # Demote markdown heading lines to plain text.
        line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
        cleaned_lines.append(line)

    merged = "\n".join(cleaned_lines)
    merged = re.sub(r"\n{3,}", "\n\n", merged).strip()
    return merged


def _split_sources_block(text):
    marker = "\n\n---\n\n### Sources\n\n"
    if marker not in text:
        return text.strip(), ""
    body, sources = text.split(marker, 1)
    return body.strip(), sources.strip()


@st.cache_resource(show_spinner=False)
def _init_backend():
    load_api_key(".env")
    main_db = load_vector_store(LEGAL_TACTICS_SCRAPED_DB_DIR)
    law_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)
    return main_db, law_db


def _ask(question, role):
    text = (question or "").strip()
    if not text:
        return

    st.session_state.messages.append({"role": "user", "content": text})
    vector_db, scraped_vector_db = st.session_state.vector_db, st.session_state.scraped_vector_db

    if not vector_db or not scraped_vector_db:
        st.session_state.messages.append(
            {"role": "assistant", "content": "Error: Vector store not loaded. Please ensure backend setup is complete."}
        )
        st.session_state.suggestions = [
            "How do I fix missing vector store files?",
            "Which setup script should I run first?",
            "Can you verify my environment checklist?",
        ]
        return

    short_context = _history_to_context(st.session_state.messages[:-1], max_turns=3)
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
    cleaned_response = _normalize_conversational_response((response or "").strip())
    answer = _format_answer(cleaned_response, citations, role)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.suggestions = _extract_followups(cleaned_response, text, role, max_items=3)


def main():
    st.set_page_config(
        page_title="★ Star | Massachusetts Housing Law Assistant",
        page_icon="★",
        layout="wide",
        menu_items={"Get help": None, "Report a bug": None, "About": None},
    )
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "suggestions" not in st.session_state:
        st.session_state.suggestions = []
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "Dark"
    if "role_mode" not in st.session_state:
        st.session_state.role_mode = "general"
    if "vector_db" not in st.session_state or "scraped_vector_db" not in st.session_state:
        st.session_state.vector_db, st.session_state.scraped_vector_db = _init_backend()

    theme = st.session_state.theme_mode
    st.markdown(PAGE_CSS + (LIGHT_OVERRIDES if theme == "Light" else ""), unsafe_allow_html=True)
    st.markdown("<div class='app-frame'>", unsafe_allow_html=True)
    st.markdown("<div class='topbar'>", unsafe_allow_html=True)
    top_cols = st.columns([5.0, 1.1, 1.35, 0.85], gap="small")
    with top_cols[0]:
        st.markdown("<div class='brand-title'><span class='star'>★</span> Star | Massachusetts Housing Law Assistant</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>Chat naturally. Follow-up context and citations are preserved.</div>", unsafe_allow_html=True)
    with top_cols[1]:
        st.selectbox("Theme", ["Dark", "Light"], key="theme_mode", label_visibility="collapsed")
    with top_cols[2]:
        st.selectbox("Perspective", ["general", "tenant", "landlord"], key="role_mode", label_visibility="collapsed")
    with top_cols[3]:
        if st.button("Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.suggestions = []
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    role = st.session_state.role_mode
    st.markdown("<div class='chat-shell'>", unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown(
            "<div class='empty-state'>"
            "<div class='empty-title'>Welcome to ★ Star</div>"
            "<div class='empty-sub'>Ask a Massachusetts housing-law question, or start with one of these examples.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        examples = [
            "What rights do tenants have?",
            "Can my landlord increase rent?",
            "What should I do if repairs are ignored?",
        ]
        ex_cols = st.columns(3)
        for i, example in enumerate(examples):
            if ex_cols[i].button(example, key=f"ex_{i}", use_container_width=True):
                with st.spinner("Star is reviewing legal context..."):
                    _ask(example, role)
                st.rerun()
    else:
        for msg in st.session_state.messages:
            msg_role = msg.get("role", "assistant")
            css_role = "user" if msg_role == "user" else "assistant"
            body, sources = _split_sources_block(msg.get("content", "")) if msg_role == "assistant" else (msg.get("content", ""), "")
            st.markdown(
                f"<div class='msg-wrap {css_role}'><div class='msg-bubble {css_role}'>",
                unsafe_allow_html=True,
            )
            st.markdown(body, unsafe_allow_html=True)
            if sources:
                st.markdown("<div class='sources-card'><div class='sources-title'>Sources</div>", unsafe_allow_html=True)
                st.markdown(sources, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

    if st.session_state.suggestions:
        st.markdown("<div class='rec-heading'>Suggested next questions</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, suggestion in enumerate(st.session_state.suggestions):
            if suggestion:
                if cols[idx].button(suggestion, key=f"rec_{idx}", use_container_width=True):
                    with st.spinner("Star is reviewing legal context..."):
                        _ask(suggestion, role)
                    st.rerun()

    prompt = st.chat_input("Ask your question...")
    if prompt:
        with st.spinner("Star is reviewing legal context..."):
            _ask(prompt, role)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
