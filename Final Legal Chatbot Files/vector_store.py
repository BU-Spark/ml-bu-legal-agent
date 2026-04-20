import os
import re
import shutil
from copy import deepcopy

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from llm_interface import LLM
from openai_llm import OpenAILLM
from ollama_llm import OllamaLLM
from config import (
    DEFAULT_LLM,
    OPENAI_DEFAULT_MODEL,
    OLLAMA_DEFAULT_MODEL,
    FINAL_CONTEXT_K,
    DOC_COMPRESSION_MAX_SENTENCES,
    DOC_COMPRESSION_MIN_CHARS,
)
from scraping_load import combined_similarity_search_with_scores, format_context_with_sources


# --- Vector Store Management ---

def create_vector_store(chunks, persist_dir: str):
    """Create and persist a Chroma vector store using OpenAI embeddings."""
    if os.path.exists(persist_dir):
        print(f"Removing existing vector store from {persist_dir}")
        shutil.rmtree(persist_dir)

    print(f"Total chunks received for vector store: {len(chunks)}")
    if chunks:
        print(f"Example chunk: {chunks[0].page_content[:300]}")

    try:
        embedding_model = OpenAIEmbeddings()
        print(f"Building and saving the new vector store at {persist_dir} with OpenAI embeddings...")
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=persist_dir
        )
        return vector_db
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None


def load_vector_store(persist_dir: str):
    """Load an existing Chroma vector store."""
    try:
        embedding_model = OpenAIEmbeddings()
        vector_db = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
        print(f"Vector store loaded from {persist_dir}")
        return vector_db
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None


# --- Document Compression Helpers ---

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z']+")


def wordset(text: str) -> set:
    if not text:
        return set()
    return set(w.lower() for w in TOKEN_RE.findall(str(text)))


def split_sentences(text: str):
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def sentence_overlap_score(query: str, sentence: str) -> float:
    q = wordset(query)
    s = wordset(sentence)
    if not q:
        return 0.0
    return len(q & s) / max(1, len(q))


def compress_doc_for_query(doc, query: str, max_sentences: int = DOC_COMPRESSION_MAX_SENTENCES):
    """
    Keep short chunks unchanged; for longer chunks select the most
    query-relevant sentences plus their immediate neighbors.
    """
    doc_copy = deepcopy(doc)
    text = doc_copy.page_content or ""

    if len(text) <= DOC_COMPRESSION_MIN_CHARS:
        return doc_copy

    sentences = split_sentences(text)
    if len(sentences) <= max_sentences:
        return doc_copy

    scored = [(idx, sent, sentence_overlap_score(query, sent)) for idx, sent in enumerate(sentences)]
    scored.sort(key=lambda x: x[2], reverse=True)

    chosen = set()
    for idx, _, _ in scored[:max_sentences]:
        chosen.add(idx)
        if idx - 1 >= 0:
            chosen.add(idx - 1)
        if idx + 1 < len(sentences):
            chosen.add(idx + 1)

    compressed_text = " ".join(sentences[i] for i in sorted(chosen)).strip()
    if compressed_text:
        doc_copy.page_content = compressed_text

    return doc_copy


# --- Question Answering ---

def query_vector_store(scraped_vector_db, vector_db, query, role="general"):
    """Retrieve, rerank, compress, then generate a response with citations."""
    if vector_db is None:
        return "Error: Vector store not initialized.", []

    if DEFAULT_LLM == "openai":
        llm_engine: LLM = OpenAILLM(model_name=OPENAI_DEFAULT_MODEL)
    elif DEFAULT_LLM == "ollama":
        llm_engine: LLM = OllamaLLM(model_name=OLLAMA_DEFAULT_MODEL)
    else:
        raise ValueError(f"Unsupported LLM type: {DEFAULT_LLM}")

    # Stage 1 — skip gating, use original query as-is
    standardized_query = query

    # Stage 2 — retrieve with MMR + reranker
    similar_docs, _ = combined_similarity_search_with_scores(
        scraped_db=scraped_vector_db,
        doc_db=vector_db,
        query=standardized_query,
        role=role,
        k=FINAL_CONTEXT_K,
    )

    if not similar_docs:
        return "Sorry, I couldn't find enough relevant information to answer that question.", []

    # Stage 3 — compress each chunk to its most relevant sentences
    compressed_docs = [
        compress_doc_for_query(doc, standardized_query, max_sentences=DOC_COMPRESSION_MAX_SENTENCES)
        for doc in similar_docs
    ]

    # Stage 4 — format context with clickable source citations
    context, citations = format_context_with_sources(compressed_docs)

    # Stage 5 — generate answer
    try:
        if DEFAULT_LLM == "openai":
            response = llm_engine.generate_response(
                question=standardized_query, context=context, role=role,
            )
        else:
            response = llm_engine.generate_response(
                question=standardized_query, context=context,
            )
        return response.strip(), citations
    except Exception as e:
        print(f"Error during LLM query: {e}")
        return "Sorry, there was an error processing your request.", []
