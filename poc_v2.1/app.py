import gradio as gr
import os
from config import load_api_key, VECTOR_DB_DIR, SCRAPED_VECTOR_DB_DIR
from vector_store import load_vector_store, query_vector_store

# Load API key and vector store on startup
load_api_key()
vector_db = load_vector_store(VECTOR_DB_DIR)
scraped_vector_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)

def ask_star(user_query, role):
    if not vector_db:
        return "Error: Vector store not loaded. Please ensure the backend is set up correctly."

    refusal = (
        "Sorry, I can't answer that question. I can only answer questions about Massachusetts tenant law. "
        "I may have misunderstood you, so try to phrase your input as a simple question."
    )

    # 1) First attempt (requested role)
    response, citations = query_vector_store(scraped_vector_db, vector_db, user_query, role=role)
    citation_text = "\n".join(f"• {c}" for c in citations) if citations else ""

    # 2) If we got the refusal but we DO have citations, it's likely a false refusal.
    #    Retry in GENERAL mode (neutral) to avoid role-guard bugs.
    if response.strip() == refusal and citations:
        response2, citations2 = query_vector_store(scraped_vector_db, vector_db, user_query, role="general")
        # Prefer retry result if it is not the same refusal
        if response2.strip() != refusal:
            response, citations = response2, citations2
            citation_text = "\n".join(f"• {c}" for c in citations) if citations else ""

    # 3) Render output
    if citations:
        return f"{response}\n\n📚 Sources:\n{citation_text}"
    return response

if __name__ == "__main__":
    iface = gr.Interface(
        fn=ask_star,
        inputs=[
            gr.Textbox(label="Ask Star a question about Massachusetts tenant law:"),
            gr.Dropdown(
                choices=["general", "tenant", "landlord"],
                label="Specify your role (optional):",
                value="general"  # Default role
            ),
        ],
        outputs=gr.Textbox(label="Star's Response:"),
        title="Star - Massachusetts Tenant Law Expert",
        description="Ask Star any question you have about tenant law in Massachusetts and she will provide an expert answer based on the provided documents.",
    )
    iface.launch(server_name="0.0.0.0", server_port=7860) # Make it accessible on your network