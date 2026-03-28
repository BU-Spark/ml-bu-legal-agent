from typing import List, Tuple
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

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


def dedupe_documents(docs: List[Document]) -> List[Document]:
    seen = set()
    deduped = []

    for doc in docs:
        md = doc.metadata or {}
        source = md.get("source", "")
        section_name = md.get("section_name", "")
        text_key = (doc.page_content or "")[:350].strip()

        key = (source, section_name, text_key)
        if key not in seen:
            seen.add(key)
            deduped.append(doc)

    return deduped


def split_docs_by_role(docs: List[Document], role: str):
    if not role or role == "general":
        return docs, []

    role_docs = []
    other_docs = []

    for doc in docs:
        doc_role = (doc.metadata or {}).get("role", "general")
        if doc_role == role:
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

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: float(x[1]),
        reverse=True,
    )

    ranked_docs = [doc for doc, _ in ranked]
    ranked_scores = [float(score) for _, score in ranked]
    return ranked_docs, ranked_scores


def threshold_reranked_docs(
    docs: List[Document],
    scores: List[float],
    min_score: float,
    top_k: int,
) -> Tuple[List[Document], List[float]]:
    if not docs:
        return [], []

    kept_docs = []
    kept_scores = []

    for doc, score in zip(docs, scores):
        if score >= min_score:
            kept_docs.append(doc)
            kept_scores.append(score)

    # fallback so recall does not collapse
    if len(kept_docs) == 0:
        fallback_k = min(top_k, len(docs))
        return docs[:fallback_k], scores[:fallback_k]

    return kept_docs[:top_k], kept_scores[:top_k]


def retrieve_legal_tactics_candidates(doc_db, query: str, role: str | None):
    """
    Retrieve a wider LT candidate pool, then softly favor role-matched chunks
    without dropping too much general-context support.
    """
    docs_lt = doc_db.max_marginal_relevance_search(
        query,
        k=LEGAL_TACTICS_K,
        fetch_k=LEGAL_TACTICS_FETCH_K,
    )
    docs_lt = dedupe_documents(docs_lt)

    if not role or role == "general":
        return docs_lt

    role_docs, other_docs = split_docs_by_role(docs_lt, role)

    # Preserve role-specific evidence first, but keep general chunks too.
    # This helps tenant/landlord mode without killing recall.
    mixed = role_docs[: max(MIN_LT_RESULTS, LEGAL_TACTICS_K // 2)] + other_docs
    mixed = dedupe_documents(mixed)

    # If role filtering was too sparse, fall back to original set.
    if len(role_docs) < MIN_LT_RESULTS:
        return docs_lt

    return mixed


def retrieve_law_candidates(scraped_db, query: str):
    docs_law = scraped_db.max_marginal_relevance_search(
        query,
        k=SCRAPED_LAW_K,
        fetch_k=SCRAPED_LAW_FETCH_K,
    )
    docs_law = dedupe_documents(docs_law)

    if len(docs_law) < MIN_LAW_RESULTS:
        return docs_law

    return docs_law[: max(SCRAPED_LAW_K, MIN_LAW_RESULTS)]


def combined_similarity_search(scraped_db, doc_db, query, role=None, k=FINAL_CONTEXT_K):
    docs, _ = combined_similarity_search_with_scores(
        scraped_db=scraped_db,
        doc_db=doc_db,
        query=query,
        role=role,
        k=k,
    )
    return docs


def combined_similarity_search_with_scores(scraped_db, doc_db, query, role=None, k=FINAL_CONTEXT_K):
    # 1) Retrieve candidate pools
    docs_lt = retrieve_legal_tactics_candidates(doc_db, query, role=role)
    docs_law = retrieve_law_candidates(scraped_db, query)

    # 2) Merge all candidates, then global rerank
    candidate_docs = dedupe_documents(docs_lt + docs_law)
    ranked_docs, ranked_scores = rerank_documents(query, candidate_docs)

    # 3) Apply threshold with fallback
    final_docs, final_scores = threshold_reranked_docs(
        ranked_docs,
        ranked_scores,
        min_score=RERANK_MIN_SCORE,
        top_k=max(k, MIN_LT_RESULTS + MIN_LAW_RESULTS),
    )

    # 4) Final balancing pass:
    #    - for general: purely top-k after rerank
    #    - for tenant/landlord: try to keep at least one role-matched LT doc if available
    if role and role != "general":
        role_docs = []
        non_role_docs = []

        for doc, score in zip(final_docs, final_scores):
            doc_role = (doc.metadata or {}).get("role", "general")
            source = (doc.metadata or {}).get("source", "")
            is_lt = source.lower().endswith(".pdf")

            if is_lt and doc_role == role:
                role_docs.append((doc, score))
            else:
                non_role_docs.append((doc, score))

        balanced_docs = []
        balanced_scores = []

        # guarantee one role-matched LT chunk if possible
        if role_docs:
            balanced_docs.append(role_docs[0][0])
            balanced_scores.append(role_docs[0][1])

        for doc, score in non_role_docs:
            if len(balanced_docs) >= k:
                break
            balanced_docs.append(doc)
            balanced_scores.append(score)

        # if still short, fill from remaining role docs
        for doc, score in role_docs[1:]:
            if len(balanced_docs) >= k:
                break
            balanced_docs.append(doc)
            balanced_scores.append(score)

        final_docs, final_scores = dedupe_documents(balanced_docs), balanced_scores[: len(dedupe_documents(balanced_docs))]

    else:
        final_docs = final_docs[:k]
        final_scores = final_scores[:k]

    return final_docs[:k], final_scores[:k]


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