import os
from dotenv import load_dotenv

def load_api_key(dotenv_path="../.env"):
    load_dotenv(dotenv_path=dotenv_path)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key is None:
        print("Error: OPENAI_API_KEY not found in .env file.")
        exit()
    os.environ["OPENAI_API_KEY"] = openai_api_key
    return openai_api_key

# Define project-level constants
VECTOR_DB_DIR = os.path.join(os.getcwd(), "/chroma_db")
TEMP_PDF_DIR = "../temp_pdfs"
DATA_DIR = "../data"