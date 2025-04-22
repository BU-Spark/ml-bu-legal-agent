# import gradio as gr
# import os
# from config import load_api_key, VECTOR_DB_DIR
# from vector_store import load_vector_store, query_vector_store
# from combined_query_engine import ask_combined_question

# # Load API key and vector store on startup
# load_api_key()
# vector_db = load_vector_store(VECTOR_DB_DIR)

# # def ask_star(user_query, role):
# #     """
# #     Function to handle user queries and return the agent's response.
# #     """
# #     if vector_db:
# #         #response = query_vector_store(vector_db, user_query, role=role)
# #         response, citations = ask_combined_question(user_query, role=role)
# #         response += "\n\n📚 Sources:\n" + "\n".join(f"• {c}" for c in citations)
# #         return response
# #     else:
# #         return "Error: Vector store not loaded. Please ensure the backend is set up correctly."

# def ask_star(user_query, role):
#     """
#     Function to handle user queries and return the agent's response.
#     """
#     response, citations = ask_combined_question(user_query, role=role)
#     citation_text = "\n".join(f"• {c}" for c in citations)
#     return f"{response}\n\n📚 Sources:\n{citation_text}"

# if __name__ == "__main__":
#     iface = gr.Interface(
#         fn=ask_star,
#         inputs=[
#             gr.Textbox(label="Ask Star a question about Massachusetts tenant law:"),
#             gr.Dropdown(
#                 choices=["general", "tenant", "landlord"],
#                 label="Specify your role (optional):",
#                 value="general"  # Default role
#             ),
#         ],
#         outputs=gr.Textbox(label="Star's Response:"),
#         title="Star - Massachusetts Tenant Law Expert",
#         description="Ask Star any question you have about tenant law in Massachusetts and she will provide an expert answer based on the provided documents.",
#     )
#     iface.launch(server_name="0.0.0.0", server_port=7860) # Make it accessible on your network

# import gradio as gr
# from combined_query_engine import ask_combined_question
# from config import load_api_key

# # Load API key
# load_api_key()

# def ask_star(user_query, role):
#     """
#     Function to handle user queries and return the agent's response.
#     """
#     response, citations = ask_combined_question(user_query, role=role)
#     citation_text = "\n".join(f"• {c}" for c in citations)
#     return f"{response}\n\n📚 Sources:\n{citation_text}"

# if __name__ == "__main__":
#     iface = gr.Interface(
#         fn=ask_star,
#         inputs=[
#             gr.Textbox(label="Ask Star a question about Massachusetts tenant law:"),
#             gr.Dropdown(
#                 choices=["general", "tenant", "landlord"],
#                 label="Specify your role (optional):",
#                 value="general"  # Default role
#             ),
#         ],
#         outputs=gr.Textbox(label="Star's Response:"),
#         title="Star - Massachusetts Tenant Law Expert",
#         description="Ask Star any question you have about tenant law in Massachusetts and she will provide an expert answer based on the provided documents.",
#     )
#     iface.launch(server_name="0.0.0.0", server_port=7860)

import gradio as gr
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from combined_query_engine import ask_combined_question
from config import load_api_key

# Load key
load_api_key()

# def ask_star(user_query, role):
#     response, citations = ask_combined_question(user_query, role=role)
#     citation_text = "\n".join(f"• {c}" for c in citations)
#     return f"{response}\n\n📚 Sources:\n{citation_text}"

def ask_star(user_query, role):
    """
    Function to handle user queries and return the agent's response.
    """
    try:
        response, citations = ask_combined_question(user_query, role=role)
        citation_text = "\n".join(f"• {c}" for c in citations)
        return f"{response}\n\n📚 Sources:\n{citation_text}"
    except Exception as e:
        import traceback
        return f"❌ An error occurred:\n{str(e)}\n\n{traceback.format_exc()}"

if __name__ == "__main__":
    iface = gr.Interface(
        fn=ask_star,
        inputs=[
            gr.Textbox(label="Ask Star a question about Massachusetts tenant law:"),
            gr.Dropdown(
                choices=["general", "tenant", "landlord"],
                label="Specify your role (optional):",
                value="general"
            ),
        ],
        outputs=gr.Textbox(label="Star's Response:"),
        title="Star - Massachusetts Tenant Law Expert",
        description="Ask Star any question you have about tenant law in Massachusetts and she will provide an expert answer based on the provided documents.",
    )
    iface.launch(server_name="0.0.0.0", server_port=7860)
