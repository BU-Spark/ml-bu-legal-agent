import os
import shutil
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

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

def query_vector_store(vector_db, query, role="general",  k_mmr=5, fetch_k=3):
    ''' Finds the most relevant chunks based on the query.
    Switching from similarity to MMR bc MMR prioritizes diversity in the results, 
    ensuring a mix of relevant but non-redundant information, 
    whereas similarity search focuses solely on the closest matches.
    '''
    results = vector_db.max_marginal_relevance_search(query, k=k_mmr)
    filtered_results = [doc.page_content for doc in results if doc.metadata.get("role", "general") == role]

    if not filtered_results:  # Fallback if no perfect role match
        filtered_results = [doc.page_content for doc in results]

    return filtered_results[:fetch_k]  # Return only the top k results