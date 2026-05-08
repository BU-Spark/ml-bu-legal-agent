from typing import List, Tuple
from pathlib import Path
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
import re

from config import (
    USE_RERANKER,
    RERANKER_MODEL,
    LEGAL_TACTICS_K,
    SCRAPED_LAW_K,
    LEGAL_TACTICS_FETCH_K,
    SCRAPED_LAW_FETCH_K,
    FINAL_CONTEXT_K,
    RERANK_MIN_SCORE,
    MIN_LT_RESULTS,
    MIN_LAW_RESULTS,
)


_RERANKER = None


def get_reranker():
    global _RERANKER
    if _RERANKER is None and USE_RERANKER:
        print(f"Loading reranker: {RERANKER_MODEL}")
        _RERANKER = CrossEncoder(RERANKER_MODEL)
    return _RERANKER


def clean_source_name(name: str) -> str:
    """Strip 'Chapter X: ' prefix from Legal Tactics section names."""
    return re.sub(r'^Chapter\s+\d+:\s*', '', name).strip()


# Mapping from PDF filename to Legal Tactics chapter PDF URL (masslegalhelp.org 2025 edition)
LEGAL_TACTICS_URLS = {
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


def dedupe_documents(docs: List[Document]) -> List[Document]:
    seen = set()
    deduped = []
    for doc in docs:
        md = doc.metadata or {}
        key = (md.get("source", ""), md.get("section_name", ""), (doc.page_content or "")[:350].strip())
        if key not in seen:
            seen.add(key)
            deduped.append(doc)
    return deduped


def split_docs_by_role(docs: List[Document], role: str):
    if not role or role == "general":
        return docs, []
    role_docs, other_docs = [], []
    for doc in docs:
        if (doc.metadata or {}).get("role", "general") == role:
            role_docs.append(doc)
        else:
            other_docs.append(doc)
    return role_docs, other_docs


def rerank_documents(query: str, docs: List[Document]) -> Tuple[List[Document], List[float]]:
    if not docs:
        return [], []
    if not USE_RERANKER:
        return docs, [0.0] * len(docs)

    reranker = get_reranker()
    pairs = [(query, doc.page_content) for doc in docs]
    scores = reranker.predict(pairs, show_progress_bar=False)

    ranked = sorted(zip(docs, scores), key=lambda x: float(x[1]), reverse=True)
    return [d for d, _ in ranked], [float(s) for _, s in ranked]


def threshold_reranked_docs(
    docs: List[Document],
    scores: List[float],
    min_score: float,
    top_k: int,
) -> Tuple[List[Document], List[float]]:
    if not docs:
        return [], []

    kept_docs = [d for d, s in zip(docs, scores) if s >= min_score]
    kept_scores = [s for s in scores if s >= min_score]

    if len(kept_docs) == 0:
        fallback_k = min(top_k, len(docs))
        return docs[:fallback_k], scores[:fallback_k]

    return kept_docs[:top_k], kept_scores[:top_k]


def retrieve_legal_tactics_candidates(doc_db, query: str, role):
    docs_lt = doc_db.max_marginal_relevance_search(
        query, k=LEGAL_TACTICS_K, fetch_k=LEGAL_TACTICS_FETCH_K,
    )
    for d in docs_lt:
        if d.metadata is None:
            d.metadata = {}
        d.metadata["_db"] = "lt"
    docs_lt = dedupe_documents(docs_lt)

    if not role or role == "general":
        return docs_lt

    role_docs, other_docs = split_docs_by_role(docs_lt, role)
    mixed = role_docs[: max(MIN_LT_RESULTS, LEGAL_TACTICS_K // 2)] + other_docs
    mixed = dedupe_documents(mixed)

    if len(role_docs) < MIN_LT_RESULTS:
        return docs_lt

    return mixed


def retrieve_law_candidates(scraped_db, query: str):
    docs_law = scraped_db.max_marginal_relevance_search(
        query, k=SCRAPED_LAW_K, fetch_k=SCRAPED_LAW_FETCH_K,
    )
    for d in docs_law:
        if d.metadata is None:
            d.metadata = {}
        d.metadata["_db"] = "law"
    docs_law = dedupe_documents(docs_law)

    if len(docs_law) < MIN_LAW_RESULTS:
        return docs_law

    return docs_law[: max(SCRAPED_LAW_K, MIN_LAW_RESULTS)]


def combined_similarity_search(scraped_db, doc_db, query, role=None, k=FINAL_CONTEXT_K):
    docs, _ = combined_similarity_search_with_scores(
        scraped_db=scraped_db, doc_db=doc_db, query=query, role=role, k=k,
    )
    return docs


def combined_similarity_search_with_scores(scraped_db, doc_db, query, role=None, k=FINAL_CONTEXT_K):
    docs_lt = retrieve_legal_tactics_candidates(doc_db, query, role=role)
    docs_law = retrieve_law_candidates(scraped_db, query)

    candidate_docs = dedupe_documents(docs_lt + docs_law)
    ranked_docs, ranked_scores = rerank_documents(query, candidate_docs)

    final_docs, final_scores = threshold_reranked_docs(
        ranked_docs, ranked_scores,
        min_score=RERANK_MIN_SCORE,
        top_k=max(k, MIN_LT_RESULTS + MIN_LAW_RESULTS),
    )

    if role and role != "general":
        role_docs, non_role_docs = [], []
        for doc, score in zip(final_docs, final_scores):
            is_lt = (doc.metadata or {}).get("source", "").lower().endswith(".pdf")
            if is_lt and (doc.metadata or {}).get("role", "general") == role:
                role_docs.append((doc, score))
            else:
                non_role_docs.append((doc, score))

        balanced_docs, balanced_scores = [], []
        if role_docs:
            balanced_docs.append(role_docs[0][0])
            balanced_scores.append(role_docs[0][1])

        for doc, score in non_role_docs:
            if len(balanced_docs) >= k:
                break
            balanced_docs.append(doc)
            balanced_scores.append(score)

        for doc, score in role_docs[1:]:
            if len(balanced_docs) >= k:
                break
            balanced_docs.append(doc)
            balanced_scores.append(score)

        final_docs = dedupe_documents(balanced_docs)
        final_scores = balanced_scores[: len(final_docs)]
    else:
        final_docs = final_docs[:k]
        final_scores = final_scores[:k]

    return final_docs[:k], final_scores[:k]


def format_context_with_sources(docs):
    """Build LLM context string and clickable Markdown citation list."""
    combined_context = ""
    citations = []
    seen_sources = set()
    citation_index = 1

    for doc in docs:
        content = doc.page_content
        source = doc.metadata.get("source", "Unknown Source")
        name = clean_source_name(doc.metadata.get("section_name", doc.metadata.get("source", "Unknown")))

        # Use section_url (scraped MA laws) or look up PDF URL from filename mapping
        url = doc.metadata.get("section_url", "")
        if not url:
            pdf_filename = Path(source).name
            url = LEGAL_TACTICS_URLS.get(pdf_filename, "")

        if url:
            combined_context += f"\n\n=== Source [{citation_index}]: {name} | URL: {url} ===\n{content}"
        else:
            combined_context += f"\n\n=== Source [{citation_index}]: {name} ===\n{content}"

        if name not in seen_sources:
            seen_sources.add(name)
            if url:
                citations.append(f"[{citation_index}] [{name}]({url})")
            else:
                citations.append(f"[{citation_index}] {name} ({source})")

        citation_index += 1

    return combined_context.strip(), citations
