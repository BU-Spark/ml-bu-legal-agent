import os
from dotenv import load_dotenv


def load_api_key(dotenv_path="../.env"):
    load_dotenv(dotenv_path=dotenv_path, override=True)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key is None:
        print("Error: OPENAI_API_KEY not found in .env file.")
        exit()
    os.environ["OPENAI_API_KEY"] = openai_api_key
    return openai_api_key


# -----------------------------
# Paths
# -----------------------------
VECTOR_DB_DIR = os.path.expanduser("~/poc_chroma/chroma_db")
SCRAPED_VECTOR_DB_DIR = os.path.expanduser("~/poc_chroma/scraped_chroma_db")
LEGAL_TACTICS_SCRAPED_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "legal_tactics_chroma_db")
TEMP_PDF_DIR = "../temp_pdfs"
DATA_DIR = "../data/Legal-Tactics-Book.zip"


# -----------------------------
# Model selection
# -----------------------------
DEFAULT_LLM = "openai"
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
OLLAMA_DEFAULT_MODEL = "deepseek-r1:1.5b"


# -----------------------------
# Reranker
# -----------------------------
USE_RERANKER = True
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


# -----------------------------
# Retrieval pool sizes
# These control how many candidates are
# fetched before reranking.
# -----------------------------
LEGAL_TACTICS_K = 10
SCRAPED_LAW_K = 10
LEGAL_TACTICS_FETCH_K = 24
SCRAPED_LAW_FETCH_K = 24


# -----------------------------
# Final number of chunks passed
# to the LLM after reranking
# -----------------------------
FINAL_CONTEXT_K = 4


# -----------------------------
# Reranker threshold after
# global rerank
# -----------------------------
RERANK_MIN_SCORE = 0.20


# -----------------------------
# Minimum retained coverage
# Helps avoid recall collapse
# after role filtering or thresholding
# -----------------------------
MIN_LT_RESULTS = 0
MIN_LAW_RESULTS = 0


# -----------------------------
# Chunking
# Used when building the vector DB
# -----------------------------
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120


# -----------------------------
# Compression
# Used before passing retrieved
# chunks into the LLM
# -----------------------------
DOC_COMPRESSION_MAX_SENTENCES = 2
DOC_COMPRESSION_MIN_CHARS = 500
