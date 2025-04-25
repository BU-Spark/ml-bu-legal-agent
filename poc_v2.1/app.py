import gradio as gr
import os
from config import load_api_key, VECTOR_DB_DIR, SCRAPED_VECTOR_DB_DIR
from vector_store import load_vector_store, query_vector_store

# Load API key and vector store on startup
load_api_key()
vector_db = load_vector_store(VECTOR_DB_DIR)
scraped_vector_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)

def ask_star(user_query, role):
    """
    Function to handle user queries and return the agent's response.
    """
    if vector_db:
        response, citations = query_vector_store(scraped_vector_db, vector_db, user_query, role=role)
        citation_text = "\n".join(f"• {c}" for c in citations)
        if response == "Sorry, I can't answer that question. I can only answer questions about Massachusetts tenant law. I may have misunderstood you, so try to phrase your input as a simple question.":
            return response
        return f"{response}\n\n📚 Sources:\n{citation_text}"
        # return response
    else:
        return "Error: Vector store not loaded. Please ensure the backend is set up correctly."

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