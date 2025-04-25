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
def query_vector_store(scraped_vector_db, vector_db, query, role="general",  k_retriever=5, score_threshold=0.3):
    """Queries the vector store and generates a natural language response using an LLM."""
    if vector_db is None:
        print("Error: Vector store not initialized.")
        return "Error: Vector store not initialized."

    if DEFAULT_LLM == "openai":
        llm_engine: LLM = OpenAILLM(model_name=OPENAI_DEFAULT_MODEL)
    elif DEFAULT_LLM == "ollama":
        llm_engine: LLM = OllamaLLM(model_name=OLLAMA_DEFAULT_MODEL)
    else:
        raise ValueError(f"Unsupported LLM type: {DEFAULT_LLM}")

    search_kwargs = {
        "k": k_retriever,
        "score_threshold": score_threshold
    }
    if role != "general":
        search_kwargs["filter"] = {"role": role}

    retriever = vector_db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs=search_kwargs
    )

    scraped_retriever = scraped_vector_db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs=search_kwargs
    )

    standardized_query = llm_engine.standardize_query(query)

    similar_docs = combined_similarity_search(scraped_vector_db, vector_db, standardized_query, role, k_retriever)

    context, citations = format_context_with_sources(similar_docs)
    try:
        response = llm_engine.generate_response(question=standardized_query, context=context)
        return response.strip(), citations
    except Exception as e:
        print(f"Error during LLM query: {e}")
        return "Sorry, there was an error processing your request."



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