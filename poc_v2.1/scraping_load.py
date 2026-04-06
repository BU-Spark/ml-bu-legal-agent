from langchain_community.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai_llm import OpenAILLM

from pathlib import Path

# Mapping from PDF filename to Legal Tactics chapter URL on masslegalhelp.org
LEGAL_TACTICS_URLS = {
    # All 18 chapters — direct PDF links confirmed from masslegalhelp.org (2025 edition)
    "moving-in.pdf":                "https://www.masslegalhelp.org/sites/default/files/2025-10/01%20Moving%202025%20Updated%208-13-25.pdf",
    "tenant-screening.pdf":         "https://www.masslegalhelp.org/sites/default/files/2025-03/02%20Tenant%20Screening%202025.pdf",
    "security-deposits.pdf":        "https://www.masslegalhelp.org/sites/default/files/2025-10/03%20Security%20Deposits%202025-%20Updated%208-13-25.pdf",
    "tenancies.pdf":                "https://www.masslegalhelp.org/sites/default/files/2025-02/04%20Tenancies%202025.pdf",
    "rent.pdf":                     "https://www.masslegalhelp.org/sites/default/files/2025-02/05%20Rent%202025%20v2.pdf",
    "utilities.pdf":                "https://www.masslegalhelp.org/sites/default/files/2025-02/06%20Utilities%202025_0.pdf",
    "discrimination.pdf":           "https://www.masslegalhelp.org/sites/default/files/2025-03/07%20Discrimination%202025.pdf",
    "getting-repairs-made.pdf":     "https://www.masslegalhelp.org/sites/default/files/2025-03/08%20Getting%20Repairs%20Made%202025_0.pdf",
    "lead-poisoning.pdf":           "https://www.masslegalhelp.org/sites/default/files/2025-03/09%20Lead%20Poisoning%202025.pdf",
    "getting-organized.pdf":        "https://www.masslegalhelp.org/sites/default/files/2025-09/10%20Organizing%202025%20-%20Updated%209-17-2025.pdf",
    "moving-out.pdf":               "https://www.masslegalhelp.org/sites/default/files/2025-03/11%20Moving%20Out%202025.pdf",
    "evictions.pdf":                "https://www.masslegalhelp.org/sites/default/files/2025-03/12%20Evictions%202025.pdf",
    "taking-landlord-to-court.pdf": "https://www.masslegalhelp.org/sites/default/files/2025-03/13%20Taking%20Landlords%20to%20Court%202025.pdf",
    "using-court-system.pdf":       "https://www.masslegalhelp.org/sites/default/files/2025-03/14%20Using%20the%20Court%20System%202025.pdf",
    "rooming-houses.pdf":           "https://www.masslegalhelp.org/sites/default/files/2025-03/15%20Rooming%20Houses%202025.pdf",
    "mobile-homes.pdf":             "https://www.masslegalhelp.org/sites/default/files/2025-03/16%20Mobile%20Homes%202025.pdf",
    "condos.pdf":                   "https://www.masslegalhelp.org/sites/default/files/2025-01/17%20Condos_2025_chapter.pdf",
    "foreclosures.pdf":             "https://www.masslegalhelp.org/sites/default/files/2025-03/18%20Foreclosures%202025.pdf",
}


def expand_query_for_role(query: str, role: str | None) -> str:
    """
    Role-based query expansion to bias retrieval toward role-relevant materials.
    We only use this expanded query for retrieval (not for displaying the user's question).
    """
    q = (query or "").strip()

    if role == "tenant":
        return (
            f"{q} tenant rights remedies defenses retaliation habitability "
            f"notice to quit illegal eviction lockout utilities shutoff "
            f"security deposit rent withholding court answer timeline"
        )

    if role == "landlord":
        return (
            f"{q} landlord compliance lawful eviction procedure "
            f"notice to quit summary process filing service requirements "
            f"rent demand notice lease violation notice timing documentation "
            f"avoid self-help eviction retaliation discrimination"
        )

    return f"{q} Massachusetts eviction notice requirements notice to quit summary process"


def interleave_docs(docs_law, docs_lt, k):
    merged = []
    max_len = max(len(docs_law), len(docs_lt))

    for i in range(max_len):
        if i < len(docs_law):
            merged.append(docs_law[i])
        if i < len(docs_lt):
            merged.append(docs_lt[i])
        if len(merged) >= k:
            break

    return merged[:k]


def extract_pdf_title(page_content, fallback):
    for line in (page_content or "").splitlines():
        line = line.strip()
        if line.startswith("##"):
            title = line.lstrip("#").strip()
            if title:
                return title
    return fallback


def combined_similarity_search(scraped_db, doc_db, query, role=None, k=5):
    lt_vs = doc_db
    law_vs = scraped_db
    if role and role != "general":
        # Filter for role-specific results in Legal Tactics
        raw_lt = lt_vs.similarity_search_with_score(query, k=15)
        docs_lt = [doc for doc, score in raw_lt if doc.metadata.get("role", "") == role][:k]
    else:
        docs_lt = lt_vs.similarity_search(query, k=k)


    expanded_query = expand_query_for_role(query, role)

    raw_lt = lt_vs.similarity_search_with_score(expanded_query, k=25)
    if role and role != "general":
        docs_role = [doc for doc, score in raw_lt if doc.metadata.get("role", "") == role]
        if docs_role:
            docs_lt = docs_role[:k]
        else:
            docs_lt = [doc for doc, score in raw_lt][:k]
    else:
        docs_lt = [doc for doc, score in raw_lt][:k]

    docs_law = law_vs.similarity_search(expanded_query, k=k)

    return interleave_docs(docs_law, docs_lt, k)


def format_context_with_sources(docs):
    combined_context = ""
    citations = []
    seen_sources = set()  # Track seen source names to avoid duplicate citations
    citation_index = 1

    for doc in docs:
        content = doc.page_content
        source = doc.metadata.get("source", "Unknown Source")
        name = doc.metadata.get("section_name", doc.metadata.get("source", "Unknown"))

        # Use section_url for scraped laws, or look up PDF URL from mapping
        url = doc.metadata.get("section_url", "")
        if not url:
            pdf_filename = Path(source).name
            url = LEGAL_TACTICS_URLS.get(pdf_filename, "")

        # Always include content in context for LLM (better answer quality)
        if url:
            combined_context += f"\n\n=== Source [{citation_index}]: {name} | URL: {url} ===\n{content}"
        else:
            combined_context += f"\n\n=== Source [{citation_index}]: {name} ===\n{content}"

        # Only add citation once per unique source name
        if name not in seen_sources:
            seen_sources.add(name)
            if url:
                citations.append(f"[{citation_index}] [{name}]({url})")
            else:
                citations.append(f"[{citation_index}] {name} ({source})")

        citation_index += 1

    return combined_context.strip(), citations
