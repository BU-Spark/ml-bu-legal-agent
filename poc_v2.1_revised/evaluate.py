import re
import json
import ast
import numpy as np
import pandas as pd

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from vector_store import (
    load_vector_store,
    query_vector_store,
    compress_doc_for_query,
)
from config import (
    VECTOR_DB_DIR,
    SCRAPED_VECTOR_DB_DIR,
    DOC_COMPRESSION_MAX_SENTENCES,
)
from scraping_load import combined_similarity_search_with_scores


vector_db = load_vector_store(VECTOR_DB_DIR)
scraped_vector_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)


pdf_categories = [
    "tenant-screening.pdf",
    "getting-organized.pdf",
    "tenancies.pdf",
    "moving-out.pdf",
    "moving-in.pdf",
    "foreclosures.pdf",
    "security-deposits.pdf",
    "lead-poisoning.pdf",
    "using-court-system.pdf",
    "discrimination.pdf",
    "rooming-houses.pdf",
    "mobile-homes.pdf",
    "getting-repairs-made.pdf",
    "condos.pdf",
    "rent.pdf",
    "taking-landlord-to-court.pdf",
    "evictions.pdf",
    "utilities.pdf",
]


PDF_QUESTIONS = {
    "tenant-screening.pdf": [
        "What is a tenant screening report, and how can a tenant correct errors or old information in it?",
        "How can eviction history, rental history, or criminal records affect tenant screening?",
        "What rights or protections do applicants have during tenant screening, including protections for survivors of domestic violence or against discrimination?",
    ],

    "getting-organized.pdf": [
        "Why should tenants organize, and what legal right do tenants have to organize?",
        "What are the first practical steps in building a tenant group and developing a plan?",
        "What tactics can a tenant group use to address bad conditions, harassment, foreclosure, or unfair rent increases?",
    ],

    "tenancies.pdf": [
        "What kinds of tenancies are discussed in this chapter, and how do they differ?",
        "What rights or rules apply to tenants with leases compared with tenants at will?",
        "What is a tenant at sufferance, and what other non-traditional housing situations are discussed here?",
    ],

    "moving-out.pdf": [
        "What responsibilities does a tenant have when moving out if they have a lease or if they do not have a lease?",
        "What are the risks of leaving without proper notice?",
        "What is the difference between subletting an apartment and assigning a lease?",
    ],

    "moving-in.pdf": [
        "What should a tenant do before renting an apartment, including checking the apartment and learning about the landlord?",
        "What should a tenant look for in a lease, including illegal clauses or unfair terms?",
        "What charges can a landlord legally collect before move-in, and why is it important to get receipts and promises in writing?",
    ],

    "foreclosures.pdf": [
        "What should a tenant do first if they learn their building may be in foreclosure?",
        "What options can a tenant have after a foreclosure, including staying, leaving, or taking cash for keys?",
        "What should a tenant know about utilities, repairs, eviction, and getting a security deposit back after foreclosure?",
    ],

    "security-deposits.pdf": [
        "How much can a landlord lawfully request at move-in for a security deposit, last month's rent, and other charges?",
        "What are a landlord's responsibilities for receipts, statement of condition, bank account, interest, and records for a security deposit?",
        "When can a tenant get a security deposit back, and what may the landlord lawfully use it for?",
    ],

    "lead-poisoning.pdf": [
        "What protections do tenants have under Massachusetts lead law?",
        "What right does a tenant have to know about lead hazards before renting?",
        "How can a tenant get a home inspected or deleaded, and what protections exist against retaliation?",
    ],

    "using-court-system.pdf": [
        "What courts may hear housing-related cases in Massachusetts, and how are they different?",
        "What legal help, mediation, and court resources are available to tenants using the court system?",
        "What should a tenant know about filing or defending civil and criminal housing-related cases in court?",
    ],

    "discrimination.pdf": [
        "What kinds of housing discrimination are illegal under Massachusetts and federal law?",
        "Who is protected against housing discrimination, and what housing is covered by those laws?",
        "What steps should a tenant take if they think they have been discriminated against in housing?",
    ],

    "rooming-houses.pdf": [
        "What is a rooming house, and what licensing requirements apply to it?",
        "What special housing conditions apply in rooming houses, including cooking, bathroom, and floor-space rules?",
        "What rights do rooming house residents have, including rights based on how long they have lived there?",
    ],

    "mobile-homes.pdf": [
        "What should a person know about buying or selling a mobile home in a park?",
        "What rules apply when becoming a mobile home park tenant, including park rules and required notices?",
        "What protections apply to rent increases, park conditions, park closings or sales, and eviction in mobile home parks?",
    ],

    "getting-repairs-made.pdf": [
        "What rights does a tenant have to a decent place to live, including sanitary code, habitability, and quiet enjoyment?",
        "How should a tenant document repair problems and establish that the landlord knew about the conditions?",
        "What options does a tenant have if a landlord refuses to make repairs, including inspections, rent withholding, repair and deduct, court, or receivership?",
    ],

    "condos.pdf": [
        "What protections do tenants have when a landlord wants to convert a building into condominiums?",
        "What notice, right-to-purchase, rent protection, and moving-expense protections may apply during condo conversion?",
        "What protections exist for tenants who are already living in condos or in places being converted to condos?",
    ],

    "rent.pdf": [
        "What counts as rent, and what should tenants know about rent receipts and disputes about the amount of rent?",
        "What happens if rent is late, and what options may help stop an eviction for nonpayment or late payment?",
        "What notice rules apply to rent increases for tenants with leases, tenants at will, and tenants in subsidized or public housing?",
    ],

    "taking-landlord-to-court.pdf": [
        "When should a tenant consider taking a landlord to court instead of trying to solve the problem outside court?",
        "Who should a tenant sue, and how can they find out who owns the building?",
        "What legal grounds may support a civil or criminal case against a landlord?",
    ],

    "evictions.pdf": [
        "When can a landlord evict a tenant, and when is eviction illegal?",
        "What notice rules apply before an eviction case can go to court, including notice to quit and nonpayment cases?",
        "What options can help a tenant stop, fight, or delay an eviction before or during court?",
    ],

    "utilities.pdf": [
        "Who pays for utilities in different housing situations, and what rights does a tenant have to obtain utility service?",
        "What protections exist against utility shut-offs, including protections for illness, winter, infants, or elderly households?",
        "What can a tenant do to restore service if utilities were shut off improperly or if a landlord failed to pay?",
    ],
}


OOD_QUESTIONS = [
    "Does Massachusetts have statewide rent control right now?",
    "What are the rules for ending a month-to-month tenancy in California?",
]


def infer_pdf_from_source(source: str) -> str:
    if not source:
        return "unknown"
    s = str(source).lower()
    m = re.search(r"([^/]+\.pdf)$", s)
    return m.group(1) if m else "unknown"


def infer_category_from_doc(doc) -> str:
    md = doc.metadata or {}
    src = md.get("source") or md.get("file") or md.get("filename") or md.get("document") or ""
    return infer_pdf_from_source(src)


def join_contexts(contexts) -> str:
    return "\n\n---\n\n".join(contexts or [])


def doc_to_text(doc) -> str:
    return (doc.page_content or "").strip()


def docs_to_texts(docs) -> list[str]:
    return [doc_to_text(d) for d in docs if doc_to_text(d)]


def get_eval_contexts(question, k=4):
    raw_docs, rerank_scores = combined_similarity_search_with_scores(
        scraped_db=scraped_vector_db,
        doc_db=vector_db,
        query=question,
        role=None,
        k=k,
    )

    compressed_docs = [
        compress_doc_for_query(doc, question, max_sentences=DOC_COMPRESSION_MAX_SENTENCES)
        for doc in raw_docs
    ]

    raw_contexts = docs_to_texts(raw_docs)
    compressed_contexts = docs_to_texts(compressed_docs)
    retrieved_cats = [infer_category_from_doc(d) for d in raw_docs]

    return {
        "raw_docs": raw_docs,
        "compressed_docs": compressed_docs,
        "raw_contexts": raw_contexts,
        "compressed_contexts": compressed_contexts,
        "retrieved_categories": retrieved_cats,
        "rerank_scores": rerank_scores,
    }


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z']+")


def wordset(text: str) -> set:
    if not text:
        return set()
    return set(w.lower() for w in TOKEN_RE.findall(str(text)))


emb = OpenAIEmbeddings()


def cosine(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return float(np.dot(a, b) / denom)


def retrieval_recall(question: str, contexts: list[str]) -> float:
    if not contexts:
        return 0.0
    q = wordset(question)
    if not q:
        return 0.0
    ctx = wordset(join_contexts(contexts))
    return float(len(q & ctx) / len(q))


def answer_relevancy(question: str, answer: str) -> float:
    if not answer:
        return 0.0
    qv = emb.embed_query(question)
    av = emb.embed_query(answer)
    return cosine(qv, av)


def top1_support_score(question: str, top1_context: str) -> float:
    if not top1_context:
        return 0.0
    q = wordset(question)
    c = wordset(top1_context)
    if not q:
        return 0.0
    return float(len(q & c) / len(q))


judge = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM = """You are a strict evaluator for RAG answers.

Given QUESTION, ANSWER, and CONTEXTS, judge whether the ANSWER is supported by the CONTEXTS.

Return JSON only with keys:
- grounded_score: number from 0 to 1
- notes: short string

Scoring guidance:
- 1.0 = every important claim in the answer is directly supported by the contexts
- 0.7-0.9 = mostly supported, minor unsupported wording or mild overreach
- 0.4-0.6 = partially supported, some unsupported claims or missing evidence
- 0.1-0.3 = weak support, major unsupported content
- 0.0 = answer is unsupported or contradicted by the contexts
"""


def _parse_json(response_text: str) -> dict:
    response = (response_text or "").strip()

    try:
        return json.loads(response)
    except Exception:
        pass

    try:
        return ast.literal_eval(response)
    except Exception:
        pass

    start = response.find("{")
    end = response.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = response[start:end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            try:
                return ast.literal_eval(snippet)
            except Exception:
                pass

    return {"grounded_score": 0.0, "notes": "Could not parse evaluator output."}


def judge_grounding(question, answer, contexts):
    context_text = join_contexts(contexts)[:7000]
    messages = [
        SystemMessage(content=SYSTEM),
        HumanMessage(
            content=(
                f"QUESTION:\n{question}\n\n"
                f"ANSWER:\n{answer}\n\n"
                f"CONTEXTS:\n{context_text}"
            )
        )
    ]
    response = judge.invoke(messages).content.strip()
    return _parse_json(response)


def build_eval_questions(include_ood: bool = False):
    eval_questions = []

    for pdf in pdf_categories:
        questions = PDF_QUESTIONS.get(pdf, [])
        for q in questions:
            eval_questions.append((pdf, q, 0))

    if include_ood:
        for pdf in pdf_categories:
            for q in OOD_QUESTIONS:
                eval_questions.append((pdf, q, 1))

    seen = set()
    deduped = []
    for cat, q, is_ood in eval_questions:
        key = (cat, q, is_ood)
        if key not in seen:
            seen.add(key)
            deduped.append((cat, q, is_ood))

    return deduped


eval_questions = build_eval_questions(include_ood=False)

print(f"PDF categories: {len(pdf_categories)}")
print(f"Total evaluation questions: {len(eval_questions)}")


RECALL_BAD = 0.25
TOP1_BAD = 0.25
GROUNDED_BAD = 0.70
RELEVANCY_BAD = 0.60


def what_to_improve(rr: float, top1: float, ar: float, grounded: float) -> str:
    issues = []

    if top1 < TOP1_BAD:
        issues.append("Top retrieved chunk weak -> improve retrieval or reranker ranking")

    if rr < RECALL_BAD:
        issues.append("Retrieval coverage low -> improve chunking, fetch_k, or candidate diversity")

    if grounded < GROUNDED_BAD:
        issues.append("Groundedness low -> improve evidence selection or reduce unsupported synthesis")

    if ar < RELEVANCY_BAD:
        issues.append("Answer relevancy low -> answer may be generic or off-topic")

    return " | ".join(issues) if issues else "OK: compare against previous run and expand eval set"


rows = []

for idx, (expected_cat, q, is_ood) in enumerate(eval_questions, start=1):
    print(f"[{idx}/{len(eval_questions)}] Evaluating {expected_cat}: {q[:100]}")

    ctx = get_eval_contexts(q, k=4)

    raw_contexts = ctx["raw_contexts"]
    compressed_contexts = ctx["compressed_contexts"]
    retrieved_cats = ctx["retrieved_categories"]
    rerank_scores = ctx["rerank_scores"]

    answer, citations = query_vector_store(
        scraped_vector_db,
        vector_db,
        q,
        role="general",
    )

    rr = retrieval_recall(q, raw_contexts)

    top1_context = raw_contexts[0] if raw_contexts else ""
    top1_score = top1_support_score(q, top1_context)
    top1_support = int(top1_score >= 0.30)

    ar = answer_relevancy(q, answer)

    judge_result = judge_grounding(q, answer, compressed_contexts)
    grounded_score = float(judge_result.get("grounded_score", 0.0))
    judge_notes = judge_result.get("notes", "")

    rows.append({
        "expected_category": expected_cat,
        "question": q,
        "answer": answer,
        "citations": citations,
        "raw_contexts": raw_contexts,
        "compressed_contexts": compressed_contexts,
        "retrieved_categories": retrieved_cats,
        "rerank_scores": rerank_scores,
        "retrieval_recall": rr,
        "top1_support_score": top1_score,
        "top1_support": top1_support,
        "answer_relevancy": ar,
        "grounded_score": grounded_score,
        "judge_notes": judge_notes,
        "what_to_improve": what_to_improve(rr, top1_score, ar, grounded_score),
        "is_ood_question": is_ood,
    })


df = pd.DataFrame(rows)


def ood_mean(series, df_all):
    mask = (df_all.loc[series.index, "is_ood_question"] == 1)
    if np.any(mask):
        return float(np.mean(series[mask]))
    return np.nan


summary = df.groupby("expected_category").agg(
    n=("question", "count"),
    retrieval_recall=("retrieval_recall", "mean"),
    top1_support_rate=("top1_support", "mean"),
    top1_support_score=("top1_support_score", "mean"),
    answer_relevancy=("answer_relevancy", "mean"),
    grounded_score=("grounded_score", "mean"),
    ood_retrieval_recall=("retrieval_recall", lambda x: ood_mean(x, df)),
    ood_top1_support_rate=("top1_support", lambda x: ood_mean(x, df)),
    ood_answer_relevancy=("answer_relevancy", lambda x: ood_mean(x, df)),
    ood_grounded_score=("grounded_score", lambda x: ood_mean(x, df)),
).reset_index()

summary = pd.merge(
    pd.DataFrame({"expected_category": pdf_categories}),
    summary,
    on="expected_category",
    how="left",
)

summary["what_to_improve"] = summary.apply(
    lambda r: what_to_improve(
        float(r["retrieval_recall"]) if pd.notna(r["retrieval_recall"]) else 0.0,
        float(r["top1_support_score"]) if pd.notna(r["top1_support_score"]) else 0.0,
        float(r["answer_relevancy"]) if pd.notna(r["answer_relevancy"]) else 0.0,
        float(r["grounded_score"]) if pd.notna(r["grounded_score"]) else 0.0,
    ),
    axis=1,
)

summary_sorted = summary.sort_values(
    by=["grounded_score", "top1_support_rate", "retrieval_recall", "answer_relevancy"],
    ascending=[True, True, True, True],
    na_position="last",
)

print("\nSUMMARY (worst grounded score first):\n")
print(summary_sorted[[
    "expected_category",
    "n",
    "top1_support_rate",
    "retrieval_recall",
    "grounded_score",
    "answer_relevancy",
    "what_to_improve"
]])

print("\n=== OVERALL AVERAGES ===")
print("avg_retrieval_recall:", round(df["retrieval_recall"].mean(), 4))
print("avg_answer_relevancy:", round(df["answer_relevancy"].mean(), 4))
print("avg_grounded_score:", round(df["grounded_score"].mean(), 4))
print("avg_top1_support_rate:", round(df["top1_support"].mean(), 4))
print("avg_top1_support_score:", round(df["top1_support_score"].mean(), 4))

# ood_df = df[df["is_ood_question"] == 1]
# if len(ood_df) > 0:
#     print("\n=== OOD AVERAGES ===")
#     print("ood_avg_retrieval_recall:", round(ood_df["retrieval_recall"].mean(), 4))
#     print("ood_avg_answer_relevancy:", round(ood_df["answer_relevancy"].mean(), 4))
#     print("ood_avg_grounded_score:", round(ood_df["grounded_score"].mean(), 4))
#     print("ood_avg_top1_support_rate:", round(ood_df["top1_support"].mean(), 4))
#     print("ood_avg_top1_support_score:", round(ood_df["top1_support_score"].mean(), 4))

df.to_csv("evaluation_results.csv", index=False)
summary.to_csv("evaluation_summary.csv", index=False)

print("\nSaved: evaluation_results.csv, evaluation_summary.csv\n")
print(
    f"Thresholds: TOP1_BAD={TOP1_BAD}, "
    f"RECALL_BAD={RECALL_BAD}, "
    f"GROUNDED_BAD={GROUNDED_BAD}, "
    f"RELEVANCY_BAD={RELEVANCY_BAD}"
)