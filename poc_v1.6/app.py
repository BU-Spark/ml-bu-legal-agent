import gradio as gr
import os
from config import load_api_key, VECTOR_DB_DIR
from vector_store import load_vector_store, query_vector_store

# Load API key and vector store on startup
load_api_key()
vector_db = load_vector_store(VECTOR_DB_DIR)

def ask_star(user_query, role):
    """
    Function to handle user queries and return the agent's response.
    """
    if vector_db:
        response = query_vector_store(vector_db, user_query, role=role)
        return response
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