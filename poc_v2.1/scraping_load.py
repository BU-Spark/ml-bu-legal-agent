from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai_llm import OpenAILLM

from pathlib import Path


def combined_similarity_search(scraped_db, doc_db, query, role=None, k=5):
    lt_vs = doc_db
    law_vs = scraped_db
    if role:
        # Filter for role-specific results in Legal Tactics
        raw_lt = lt_vs.similarity_search_with_score(query, k=15)
        docs_lt = [doc for doc, score in raw_lt if doc.metadata.get("role", "") == role][:k]
    else:
        docs_lt = lt_vs.similarity_search(query, k=k)


    docs_law = law_vs.similarity_search(query, k=k)

    return (docs_lt + docs_law)[:k]




def format_context_with_sources(docs):
    combined_context = ""
    citations = []

    for i, doc in enumerate(docs, 1):
        content = doc.page_content
        source = doc.metadata.get("source", "Unknown Source")
        name = doc.metadata.get("section_name", doc.metadata.get("source", f"Doc {i}"))
        url = doc.metadata.get("section_url", "")

        citation = f"[{i}] {name} ({source})"
        if url:
            citation += f" — {url}"

        combined_context += f"\n\n=== Source [{i}] ===\n{content}"
        citations.append(citation)

    return combined_context.strip(), citations