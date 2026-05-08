# data_to_chroma.py
# Loads cleaned Massachusetts General Laws JSON and embeds it into the
# Chroma vector store that legal_tactics_app.py / app.py read from
# (~/poc_chroma/scraped_chroma_db), using OpenAI embeddings so it matches
# the rest of the pipeline.
#
# Input:  massachusetts_primary_laws_PERFECTION.json
# Output: ~/poc_chroma/scraped_chroma_db/   (Chroma persistent vector store)

import json
import os
import shutil

from dotenv import load_dotenv
load_dotenv(".env", override=True)

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not found. Make sure .env is in this folder.")

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


# ── Config ────────────────────────────────────────────────────────────────────
INPUT_FILE  = "massachusetts_primary_laws_PERFECTION.json"
PERSIST_DIR = os.path.expanduser("~/poc_chroma/scraped_chroma_db")
# ─────────────────────────────────────────────────────────────────────────────


# 1. Load cleaned sections
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    sections = json.load(f)

print(f"📥 Loaded {len(sections)} sections from {INPUT_FILE}")

# 2. Build LangChain Documents
documents = [
    Document(
        page_content=section["section_text"],
        metadata={
            "section_name": section["section_name"],
            "section_url":  section["section_url"],
            "source":       "Massachusetts General Laws (malegislature.gov)",
        },
    )
    for section in sections
]

# 3. Embedding model (OpenAI — matches the rest of the app)
embedding_model = OpenAIEmbeddings()

# 4. Clear old DB if it exists
if os.path.exists(PERSIST_DIR):
    shutil.rmtree(PERSIST_DIR)
    print(f"🗑️  Removed old vector store at '{PERSIST_DIR}'")

os.makedirs(os.path.dirname(PERSIST_DIR), exist_ok=True)

# 5. Create and persist Chroma vector store
print(f"⏳ Embedding {len(documents)} sections with OpenAI — this may take a minute...")
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    persist_directory=PERSIST_DIR,
)

print(f"✅ Done! {len(documents)} sections embedded and saved to '{PERSIST_DIR}'")
print("   Each section includes a direct malegislature.gov URL for clickable sources.")
