import gradio as gr
import re
import os
from config import load_api_key, SCRAPED_VECTOR_DB_DIR, LEGAL_TACTICS_SCRAPED_DB_DIR
from vector_store import load_vector_store, query_vector_store

# Load API key and vector store on startup
load_api_key(".env")
# Use scraped Legal Tactics DB (chapter-level links) instead of PDF-based DB
vector_db = load_vector_store(LEGAL_TACTICS_SCRAPED_DB_DIR)
scraped_vector_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)

def make_links_clickable(text):
    """Convert Markdown links [text](url) to HTML anchor tags that open in a new tab."""
    return re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)

def ask_star(user_query, role):
    empty = (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), "", "")
    if not user_query or not user_query.strip():
        return ("Please enter a question.",) + empty
    if vector_db:
        response, citations = query_vector_store(scraped_vector_db, vector_db, user_query, role=role)
        citations = [make_links_clickable(c) for c in citations]
        citation_text = "\n\n".join(citations)
        if response.strip().startswith("Sorry, I can't answer that question."):
            return ("\u274c " + response.strip().strip('"'),) + empty
        role_label = f"> \U0001f464 **Answering as:** {role.capitalize()}\n\n"

        followups = re.findall(r'[\u201c"\u201d]([^\u201c"\u201d]+\?)[\u201c"\u201d]', response)
        followups = followups[:2]

        response = make_links_clickable(response)
        full_response = f"{role_label}{response}\n\n---\n\n### \U0001f4da Sources\n\n{citation_text}"

        f1 = followups[0] if len(followups) >= 1 else ""
        f2 = followups[1] if len(followups) >= 2 else ""

        return (
            full_response,
            gr.update(visible=bool(f1)),
            gr.update(value=f"\U0001f4ac {f1}", visible=bool(f1)),
            gr.update(value=f"\U0001f4ac {f2}", visible=bool(f2)),
            f1,
            f2,
        )
    else:
        return ("Error: Vector store not loaded. Please ensure the backend is set up correctly.",) + empty

if __name__ == "__main__":
    with gr.Blocks(title="Star - Massachusetts Housing Law Assistant") as iface:
        gr.Markdown("# \u2b50 Star \u2014 Massachusetts Housing Law Assistant")
        gr.Markdown("Ask Star any question about Massachusetts housing law. It will answer based on official legal documents and Massachusetts General Laws.")

        with gr.Row():
            with gr.Column(scale=3):
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g. What happens if my landlord doesn't return my security deposit?",
                    lines=2
                )
            with gr.Column(scale=1):
                role_input = gr.Dropdown(
                    choices=["general", "tenant", "landlord"],
                    label="Your Role",
                    value="general"
                )

        with gr.Row():
            with gr.Column(scale=1):
                submit_btn = gr.Button("Ask Star \u2b50", variant="primary")
            with gr.Column(scale=3):
                pass

        output = gr.Markdown(label="Star's Response", sanitize_html=False)

        followup_heading = gr.Markdown("### \U0001f4ac Suggested Follow-up Questions", visible=False)
        with gr.Row():
            followup_btn1 = gr.Button(visible=False)
            followup_btn2 = gr.Button(visible=False)

        followup_state1 = gr.State("")
        followup_state2 = gr.State("")

        outputs_list = [output, followup_heading, followup_btn1, followup_btn2, followup_state1, followup_state2]

        submit_btn.click(
            fn=ask_star,
            inputs=[query_input, role_input],
            outputs=outputs_list
        )

        followup_btn1.click(
            fn=ask_star,
            inputs=[followup_state1, role_input],
            outputs=outputs_list
        )

        followup_btn2.click(
            fn=ask_star,
            inputs=[followup_state2, role_input],
            outputs=outputs_list
        )

    iface.launch(server_name="0.0.0.0", server_port=7861)
