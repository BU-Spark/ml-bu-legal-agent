import os
import shutil
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from llm_interface import LLM  # Import the LLM interface
from openai_llm import OpenAILLM
from ollama_llm import OllamaLLM
from config import DEFAULT_LLM, OPENAI_DEFAULT_MODEL, OLLAMA_DEFAULT_MODEL
from scraping_load import combined_similarity_search, format_context_with_sources
import re


# ------------------------------
# Role / Persona Enforcement
# ------------------------------
def get_role_instructions(role: str) -> str:
    role = (role or "general").strip().lower()

    if role == "tenant":
        return (
            "You are STAR in TENANT mode. Write for a tenant in Massachusetts.\n"
            "Focus on tenant protections, defenses, and practical next steps.\n"
            "Include what the tenant should do now, what to document, and key risks to watch for.\n"
            "Avoid landlord-compliance coaching.\n"
        )

    if role == "landlord":
        return (
            "You are STAR in LANDLORD mode. Answer Massachusetts landlord-tenant law questions for a landlord.\n"
            "Focus on lawful compliance steps, notice requirements, and risk avoidance.\n"
            "Include a compliance checklist and clear 'do not do' items.\n"
        )

    return (
        "You are STAR in GENERAL mode. Write neutrally for either party.\n"
        "Explain the legal rule and the process at a high level without tactical coaching.\n"
    )


def get_required_headings(role: str) -> list[str]:
    role = (role or "general").strip().lower()

    if role == "tenant":
        return ["Conclusion", "Why", "What you should do next", "What to document", "Sources"]
    if role == "landlord":
        return ["Conclusion", "Why", "Compliance checklist", "What to do", "Sources"]
    return ["Conclusion", "Why", "Process overview", "Sources"]


def build_answer_format(role: str) -> str:
    headings = get_required_headings(role)
    return (
        "Return the answer using EXACTLY these sections in this order:\n"
        + "\n".join([f"- {h}:" for h in headings])
        + "\n\nRules:\n"
          "- Conclusion must start with 'Answer: Yes' or 'Answer: No' (only one).\n"
          "- If the action is not allowed, Conclusion MUST be 'Answer: No'. Do not write 'Yes, cannot'.\n"
          "- Keep the answer specific to Massachusetts tenant law.\n"
          "- Sources must be a bullet list of ONLY the provided citations.\n"
    )


def missing_headings(text: str, headings: list[str]) -> list[str]:
    t = (text or "").lower()

    def has_heading(h: str) -> bool:
        h_l = h.lower()

        # Accept common variants
        if h_l == "conclusion":
            # Either "Conclusion:" exists OR the answer starts with "Answer: Yes/No"
            if "conclusion:" in t:
                return True
            return bool(re.search(r'^\s*answer:\s*(yes|no)\b', (text or ""), re.IGNORECASE))
        else:
            return f"{h_l}:" in t

    return [h for h in headings if not has_heading(h)]


# --- Vector Store Management ---
def create_vector_store(chunks, persist_dir: str):
    """Create and persist a Chroma vector store using OpenAI embeddings."""

    if os.path.exists(persist_dir):
        print(f"Removing existing vector store from {persist_dir}")
        shutil.rmtree(persist_dir)  # Try commenting this out if issues persist

    # Debugging info
    print(f"Total chunks received for vector store: {len(chunks)}")
    if chunks:
        print(f"Example chunk: {chunks[0].page_content[:300]}")

    try:
        # Initialize OpenAI Embeddings
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
        return None  # Return None if an error occurs


def load_vector_store(persist_dir: str):
    """Loads an existing Chroma vector store."""
    try:
        embedding_model = OpenAIEmbeddings()
        vector_db = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
        print(f"Vector store loaded from {persist_dir}")
        return vector_db
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None


# --- Question Answering with LLM ---
def query_vector_store(scraped_vector_db, vector_db, query, role="general", k_retriever=5, score_threshold=0.3):
    """Queries the vector store and generates a natural language response using an LLM."""
    if vector_db is None:
        print("Error: Vector store not initialized.")
        return "Error: Vector store not initialized.", []

    if DEFAULT_LLM == "openai":
        llm_engine: LLM = OpenAILLM(model_name=OPENAI_DEFAULT_MODEL)
    elif DEFAULT_LLM == "ollama":
        llm_engine: LLM = OllamaLLM(model_name=OLLAMA_DEFAULT_MODEL)
    else:
        raise ValueError(f"Unsupported LLM type: {DEFAULT_LLM}")

    # NOTE: You currently do retrieval via combined_similarity_search().
    # These retrievers are not used downstream; kept only if you plan to switch later.
    search_kwargs = {"k": k_retriever, "score_threshold": score_threshold}
    if role != "general":
        search_kwargs["filter"] = {"role": role}

    # Unused retrievers (safe to remove if you want)
    _ = vector_db.as_retriever(search_type="similarity_score_threshold", search_kwargs=search_kwargs)
    _ = scraped_vector_db.as_retriever(search_type="similarity_score_threshold", search_kwargs=search_kwargs)

    standardized_query = llm_engine.standardize_query(query)

    # Retrieval (multi-source)
    similar_docs = combined_similarity_search(
        scraped_vector_db,
        vector_db,
        standardized_query,
        role,
        k_retriever
    )

    context, citations = format_context_with_sources(similar_docs)

    # Role-specific enforcement
    role_instructions = get_role_instructions(role)
    format_instructions = build_answer_format(role)
    required = get_required_headings(role)

    # If your OpenAILLM supports a "system" parameter, you can pass role_instructions there instead.
    final_question = (
        f"{role_instructions}\n"
        f"{format_instructions}\n"
        f"User question: {standardized_query}"
    )

    try:
        response = llm_engine.generate_response(question=final_question, context=context).strip()

        # One retry if required headings are missing (fast enforcement)
        missing = missing_headings(response, required)
        if missing:
            fixup = (
                f"{role_instructions}\n"
                f"You missed these required sections: {', '.join(missing)}.\n"
                f"Rewrite the full answer with ALL required sections and the same facts.\n\n"
                f"{format_instructions}\n"
                f"User question: {standardized_query}"
            )
            response = llm_engine.generate_response(question=fixup, context=context).strip()

        return response, citations

    except Exception as e:
        print(f"Error during LLM query: {e}")
        return "Sorry, there was an error processing your request.", []

    # Instead of RetrievalQA, we'll manually handle the prompt and LLM call
    # relevant_docs = retriever.get_relevant_documents(standardized_query)
    # scraped_relevant_docs =scraped_retriever.get_relevant_documents(standardized_query)

    
    # context  = (relevant_docs + scraped_relevant_docs)

    # try:
    #     response = llm_engine.generate_response(question=standardized_query, context=context)
    #     return response
    # except Exception as e:
    #     print(f"Error during LLM query: {e}")
    #     return "Sorry, there was an error processing your request."