import gradio as gr
import re
import os
from config import load_api_key, VECTOR_DB_DIR, SCRAPED_VECTOR_DB_DIR
from vector_store import load_vector_store, query_vector_store

# Load API key and vector store on startup
load_api_key()
vector_db = load_vector_store(VECTOR_DB_DIR)
scraped_vector_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)

def make_links_clickable(text):
    """Convert Markdown links [text](url) to HTML anchor tags that open in a new tab."""
    return re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)

def ask_star(user_query, role):
    if vector_db:
        response, citations = query_vector_store(scraped_vector_db, vector_db, user_query, role=role)
        citations = [make_links_clickable(c) for c in citations]
        citation_text = "\n\n".join(citations)
        if "Sorry, I can't answer that question." in response:
            return "❌ " + response.strip().strip('"'), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
        role_label = f"> 👤 **Answering as:** {role.capitalize()}\n\n"

        # Extract follow-up questions BEFORE converting links (avoids HTML interfering with regex)
        followups = re.findall(r'[\u201c"\u201d]([^\u201c"\u201d]+\?)[\u201c"\u201d]', response)
        followups = followups[:2]

        response = make_links_clickable(response)
        full_response = f"{role_label}{response}\n\n---\n\n### 📚 Sources\n\n{citation_text}"

        if len(followups) >= 1:
            return full_response, gr.update(visible=True), gr.update(value=f"💬 {followups[0]}", visible=True), gr.update(value=f"💬 {followups[1]}", visible=True) if len(followups) == 2 else gr.update(visible=False)
        else:
            return full_response, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
    else:
        return "Error: Vector store not loaded. Please ensure the backend is set up correctly.", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

if __name__ == "__main__":
    with gr.Blocks(title="Star - Massachusetts Housing Law Assistant") as iface:
        gr.Markdown("# ⭐ Star — Massachusetts Housing Law Assistant")
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
                submit_btn = gr.Button("Ask Star ⭐", variant="primary")
            with gr.Column(scale=3):
                pass

        output = gr.Markdown(label="Star's Response", sanitize_html=False)

        followup_heading = gr.Markdown("### 💬 Suggested Follow-up Questions", visible=False)
        with gr.Row():
            followup_btn1 = gr.Button(visible=False)
            followup_btn2 = gr.Button(visible=False)

        submit_btn.click(
            fn=ask_star,
            inputs=[query_input, role_input],
            outputs=[output, followup_heading, followup_btn1, followup_btn2]
        )

        followup_btn1.click(
            fn=lambda q, r: ask_star(q.replace("💬 ", ""), r),
            inputs=[followup_btn1, role_input],
            outputs=[output, followup_heading, followup_btn1, followup_btn2]
        )

        followup_btn2.click(
            fn=lambda q, r: ask_star(q.replace("💬 ", ""), r),
            inputs=[followup_btn2, role_input],
            outputs=[output, followup_heading, followup_btn1, followup_btn2]
        )

    iface.launch(server_name="0.0.0.0", server_port=7860)
