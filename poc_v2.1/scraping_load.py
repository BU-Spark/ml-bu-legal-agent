from langchain_community.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai_llm import OpenAILLM

from pathlib import Path


def expand_query_for_role(query: str, role: str | None) -> str:
    """
    Role-based query expansion to bias retrieval toward role-relevant materials.
    We only use this expanded query for retrieval (not for displaying the user's question).
    """
    q = (query or "").strip()

    if role == "tenant":
        # Bias toward tenant protections, defenses, remedies, retaliation, habitability, security deposit, etc.
        return (
            f"{q} tenant rights remedies defenses retaliation habitability "
            f"notice to quit illegal eviction lockout utilities shutoff "
            f"security deposit rent withholding court answer timeline"
        )

    if role == "landlord":
        # Bias toward landlord compliance, procedure, notices, filings, and risk areas
        return (
            f"{q} landlord compliance lawful eviction procedure "
            f"notice to quit summary process filing service requirements "
            f"rent demand notice lease violation notice timing documentation "
            f"avoid self-help eviction retaliation discrimination"
        )

    # General / default: neutral legal framing
    return f"{q} Massachusetts eviction notice requirements notice to quit summary process"


def combined_similarity_search(scraped_db, doc_db, query, role=None, k=5):
    lt_vs = doc_db
    law_vs = scraped_db

    expanded_query = expand_query_for_role(query, role)

    # ---- Legal Tactics / PDF docs retrieval ----
    if role:
        raw_lt = lt_vs.similarity_search_with_score(expanded_query, k=25)
        docs_role = [doc for doc, score in raw_lt if doc.metadata.get("role", "") == role]
        if docs_role:
            docs_lt = docs_role[:k]
        else:
            docs_lt = [doc for doc, score in raw_lt][:k]

    # ---- Massachusetts law retrieval (scraped DB) ----
    # Also use expanded query to steer retrieval
    docs_law = law_vs.similarity_search(expanded_query, k=k)

    # Keep your existing behavior: merge and return top k total
    return (docs_law + docs_lt)[:k]


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