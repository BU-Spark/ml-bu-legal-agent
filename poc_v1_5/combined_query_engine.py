# combined_query_engine.py 

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai_llm import OpenAILLM

from pathlib import Path


# Loading both vector stores (Primary + Pocv1.5)

def load_all_vectorstores():
    base_path = Path(__file__).resolve().parent

    legal_tactics_vs = Chroma(
        persist_directory=str(base_path / "poc_v1_5/chroma_db"),
        embedding_function=OpenAIEmbeddings()
    )

    law_vs = Chroma(
        persist_directory=str(base_path / "Primary/massachusetts_laws_chroma_db"),
        embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    )

    return legal_tactics_vs, law_vs



# Combine search results from both stores (with role)

def combined_similarity_search(query, role=None, k=5):
    lt_vs, law_vs = load_all_vectorstores()

    if role:
        # Filter for role-specific results in Legal Tactics
        raw_lt = lt_vs.similarity_search_with_score(query, k=15)
        docs_lt = [doc for doc, score in raw_lt if doc.metadata.get("role", "") == role][:k]
    else:
        docs_lt = lt_vs.similarity_search(query, k=k)

    docs_law = law_vs.similarity_search(query, k=k)

    return (docs_lt + docs_law)[:k]


# Format context and citations

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


# Main query handler

def ask_combined_question(query, role=None):
    docs = combined_similarity_search(query, role=role, k=5)
    context, citations = format_context_with_sources(docs)

    prompt = f"""
You are a helpful legal assistant.
A user has asked the following legal question:
"{query}"

You are provided with excerpts from Massachusetts housing law and legal guidance documents.
Use these to generate a helpful, accurate, and concise response.

{context}

Only include legal facts that are supported in the above excerpts.
Clearly cite the sources.
"""

    llm = OpenAILLM(model_name="gpt-3.5-turbo")
    response = llm.generate_response(question=query, context=prompt)

    return response.strip(), citations

