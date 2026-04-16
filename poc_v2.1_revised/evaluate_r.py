import re
import pandas as pd

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


# ==============================
# Load vector stores
# ==============================
vector_db = load_vector_store(VECTOR_DB_DIR)
scraped_vector_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)


# ==============================
# 45 evaluation prompts
# ==============================
TEST_CASES = [
    {"category": "tenant", "role": "tenant", "question": "What should I do if my landlord refuses to return my security deposit?"},
    {"category": "tenant", "role": "tenant", "question": "Can I legally withhold rent if my apartment has no heat?"},
    {"category": "tenant", "role": "tenant", "question": "My landlord hasn’t fixed a leak for weeks, what are my rights?"},
    {"category": "tenant", "role": "tenant", "question": "How much notice does my landlord need before evicting me?"},
    {"category": "tenant", "role": "tenant", "question": "What happens after I get a notice to quit?"},
    {"category": "tenant", "role": "tenant", "question": "Can my landlord enter my apartment without telling me?"},
    {"category": "tenant", "role": "tenant", "question": "I never signed a lease, do I still have tenant rights?"},
    {"category": "tenant", "role": "tenant", "question": "Can I break my lease early if conditions are bad?"},
    {"category": "tenant", "role": "tenant", "question": "What can I do if my landlord shuts off utilities?"},
    {"category": "tenant", "role": "tenant", "question": "I got an eviction notice but I don’t understand it, what should I do?"},

    {"category": "landlord", "role": "landlord", "question": "How do I legally evict a tenant in Massachusetts?"},
    {"category": "landlord", "role": "landlord", "question": "What notice do I need to give before eviction?"},
    {"category": "landlord", "role": "landlord", "question": "Tenant hasn’t paid rent in two months, what are my options?"},
    {"category": "landlord", "role": "landlord", "question": "Can I evict a tenant for breaking lease rules?"},
    {"category": "landlord", "role": "landlord", "question": "What is the proper eviction process step by step?"},
    {"category": "landlord", "role": "landlord", "question": "Can I enter a tenant’s apartment for inspection?"},
    {"category": "landlord", "role": "landlord", "question": "What are my responsibilities for repairs in a rental property?"},
    {"category": "landlord", "role": "landlord", "question": "Can I keep a tenant’s security deposit for damages?"},
    {"category": "landlord", "role": "landlord", "question": "What happens if I don’t follow security deposit rules?"},
    {"category": "landlord", "role": "landlord", "question": "Can I change locks if tenant is not paying rent?"},

    {"category": "general", "role": "general", "question": "What are the main rights of tenants and landlords in Massachusetts?"},
    {"category": "general", "role": "general", "question": "What is the difference between a lease and a tenant at will?"},
    {"category": "general", "role": "general", "question": "How does the eviction process work overall?"},
    {"category": "general", "role": "general", "question": "What is rent withholding and when is it allowed?"},
    {"category": "general", "role": "general", "question": "What happens in a dispute between landlord and tenant?"},
    {"category": "general", "role": "general", "question": "What legal protections exist for housing in Massachusetts?"},
    {"category": "general", "role": "general", "question": "If a tenant says there is mold and the landlord ignores it, what legal issues can come up?"},
    {"category": "general", "role": "general", "question": "What are the legal issues when utilities get shut off in a rental property?"},
    {"category": "general", "role": "general", "question": "How do security deposit rules work in Massachusetts housing law?"},
    {"category": "general", "role": "general", "question": "What should both sides understand before an eviction case reaches court?"},
    
    # ---------- TENANT ----------
    {"category": "tenant", "role": "tenant", "question": "My landlord is increasing rent suddenly, is that allowed?"},
    {"category": "tenant", "role": "tenant", "question": "What can I do if my landlord is harassing me to leave?"},
    {"category": "tenant", "role": "tenant", "question": "Can I refuse to pay rent if my apartment is unsafe?"},
    {"category": "tenant", "role": "tenant", "question": "What happens if I stay after my lease ends without renewing?"},
    {"category": "tenant", "role": "tenant", "question": "My landlord says I damaged the apartment but I disagree, what should I do?"},

# ---------- LANDLORD ----------
    {"category": "landlord", "role": "landlord", "question": "What can I do if a tenant is damaging my property?"},
    {"category": "landlord", "role": "landlord", "question": "Can I deny a tenant for having a bad rental history?"},
    {"category": "landlord", "role": "landlord", "question": "What steps should I take before filing an eviction case?"},
    {"category": "landlord", "role": "landlord", "question": "Can I charge tenants for repairs after they move out?"},
    {"category": "landlord", "role": "landlord", "question": "What should I do if a tenant refuses to pay utilities?"},

# ---------- GENERAL ----------
    {"category": "general", "role": "general", "question": "What are the legal steps before an eviction case goes to court?"},
    {"category": "general", "role": "general", "question": "How do tenants and landlords handle repair disputes legally?"},
    {"category": "general", "role": "general", "question": "What rights do tenants have against landlord retaliation?"},
    {"category": "general", "role": "general", "question": "What legal issues arise if rent is consistently late?"},
    {"category": "general", "role": "general", "question": "How do Massachusetts laws protect both tenants and landlords during disputes?"},
]


# ==============================
# Helpers
# ==============================
def doc_to_text(doc):
    return (doc.page_content or "").strip()


def docs_to_texts(docs):
    return [doc_to_text(d) for d in docs if doc_to_text(d)]


def get_eval_contexts(question, role="general", k=4):
    raw_docs, _ = combined_similarity_search_with_scores(
        scraped_db=scraped_vector_db,
        doc_db=vector_db,
        query=question,
        role=role,
        k=k,
    )

    compressed_docs = [
        compress_doc_for_query(doc, question, max_sentences=DOC_COMPRESSION_MAX_SENTENCES)
        for doc in raw_docs
    ]

    return {
        "raw_contexts": docs_to_texts(raw_docs),
        "compressed_contexts": docs_to_texts(compressed_docs),
    }


# ==============================
# Evaluation loop
# ==============================
rows = []

for idx, case in enumerate(TEST_CASES, start=1):
    category = case["category"]
    role = case["role"]
    question = case["question"]

    print(f"[{idx}/{len(TEST_CASES)}] {role}: {question}")

    ctx = get_eval_contexts(question, role=role)

    answer, citations = query_vector_store(
        scraped_vector_db,
        vector_db,
        question,
        role=role,
    )

    rows.append({
        "category": category,
        "role": role,
        "question": question,
        "answer": answer,
        "citations": citations,
        "raw_contexts": ctx["raw_contexts"],
        "compressed_contexts": ctx["compressed_contexts"],
    })


# ==============================
# Save CSV
# ==============================
df = pd.DataFrame(rows)
df.to_csv("evaluation_clean_results_45.csv", index=False)

print("\nSaved: evaluation_clean_results.csv\n")