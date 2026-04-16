import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(dotenv_path=".env"):
        if not os.path.exists(dotenv_path):
            return False

        with open(dotenv_path, "r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

        return True

def load_api_key(dotenv_path=".env"):
    load_dotenv(dotenv_path=dotenv_path)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key is None:
        print("Error: OPENAI_API_KEY not found in .env file.")
        exit()
    os.environ["OPENAI_API_KEY"] = openai_api_key
    return openai_api_key

# Define project-level constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "chroma_db")
SCRAPED_VECTOR_DB_DIR = os.path.join(BASE_DIR, "scraped_chroma_db")
TEMP_PDF_DIR = "../temp_pdfs"
DATA_DIR = "../data/Legal-Tactics-Book.zip"
DEFAULT_LLM = "openai"
# DEFAULT_LLM = "ollama"
OPENAI_DEFAULT_MODEL = "gpt-3.5-turbo"
OLLAMA_DEFAULT_MODEL = "deepseek-r1:1.5b"
