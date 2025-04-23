# import os
# from dotenv import load_dotenv

# def load_api_key(dotenv_path="../.env"):
#     load_dotenv(dotenv_path=dotenv_path)
#     openai_api_key = os.getenv("OPENAI_API_KEY")
#     if openai_api_key is None:
#         print("Error: OPENAI_API_KEY not found in .env file.")
#         exit()
#     os.environ["OPENAI_API_KEY"] = openai_api_key
#     return openai_api_key

from dotenv import load_dotenv
import os
from pathlib import Path

def load_api_key():
    # Always resolve .env from the project root
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("❌ OPENAI_API_KEY not found in .env file.")
    
    os.environ["OPENAI_API_KEY"] = openai_api_key
    return openai_api_key

# Define project-level constants
VECTOR_DB_DIR = os.path.join(os.getcwd(), "chroma_db")
TEMP_PDF_DIR = "../temp_pdfs"
DATA_DIR = "../data/Legal-Tactics-Book.zip"
DEFAULT_LLM = "openai"
# DEFAULT_LLM = "ollama"
OPENAI_DEFAULT_MODEL = "gpt-3.5-turbo"
OLLAMA_DEFAULT_MODEL = "deepseek-r1:1.5b"