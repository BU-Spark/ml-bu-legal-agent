# legal_tactics_to_chroma.py
# Converts cleaned Legal Tactics JSON into a Chroma vector store.
# Each section gets its anchor URL stored in metadata so the chatbot
# can link users directly to the exact section on masslegalhelp.org.
#
# Input:  legal_tactics_scraped_clean.json
# Output: legal_tactics_chroma_db/   (Chroma persistent vector store)
#
# Run order: legal_tactics_scraper.py → legal_tactics_cleaner.py → legal_tactics_to_chroma.py

import json
import os
import shutil

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not found. Make sure .env is in this folder.")

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


# ── Config ────────────────────────────────────────────────────────────────────
INPUT_FILE    = "legal_tactics_scraped_clean.json"
PERSIST_DIR   = "legal_tactics_chroma_db"
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
            "source":       "Legal Tactics (masslegalhelp.org)"
        }
    )
    for section in sections
]

# 3. Embedding model
embedding_model = OpenAIEmbeddings()

# 4. Clear old DB if it exists
if os.path.exists(PERSIST_DIR):
    shutil.rmtree(PERSIST_DIR)
    print(f"🗑️  Removed old vector store at '{PERSIST_DIR}'")

# 5. Create and persist Chroma vector store
print("⏳ Embedding sections — this may take a minute...")
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    persist_directory=PERSIST_DIR
)
vectorstore.persist()

print(f"✅ Done! {len(documents)} sections embedded and saved to '{PERSIST_DIR}/'")
print("   Each section includes a direct anchor URL for clickable sources.")
