# Module imports
from config import load_api_key, VECTOR_DB_DIR, TEMP_PDF_DIR, DATA_DIR, SCRAPED_VECTOR_DB_DIR
from pdf_processing import extract_zip, process_single_pdf, determine_role
from text_processing import create_chunks_with_headers
from vector_store import create_vector_store, query_vector_store, load_vector_store, vector_store_has_embeddings
from data_to_chroma_function import create_scraped_vector_store

# Library imports
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def load_and_process_pdfs(zip_path):
    """Processes a zipped folder of PDFs, preserves headers, and splits into smaller chunks for vector storage."""
    pdf_files = extract_zip(zip_path, extract_to=TEMP_PDF_DIR)
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for pdf in pdf_files:
        page_records = process_single_pdf(pdf)
        chunk_payloads = create_chunks_with_headers(page_records, text_splitter)
        for chunk_payload in chunk_payloads:
            chunk_text = chunk_payload["page_content"]
            role = determine_role(chunk_text)
            metadata = {
                **chunk_payload["metadata"],
                "source": os.path.basename(pdf),
                "role": role,
            }
            all_chunks.append(Document(page_content=chunk_text, metadata=metadata))
    return all_chunks


def main():
    load_api_key()
    zip_file_path = DATA_DIR

    #Creating the Document DB
    if vector_store_has_embeddings(VECTOR_DB_DIR):
        print("Loading existing vector store...")
        vector_db = load_vector_store(VECTOR_DB_DIR)
    else:
        print("PDF vector store is missing or empty. Rebuilding it...")
        document_chunks = load_and_process_pdfs(zip_file_path)
        print(f"Total chunks created: {len(document_chunks)}")

        # Tests
        if document_chunks:
            print(f"Example chunk:\n{document_chunks[0].page_content[:500]}")
            print(f"Metadata: {document_chunks[0].metadata}")

        vector_db = create_vector_store(document_chunks, VECTOR_DB_DIR)
        
        if vector_db:
            print(f"Vector store successfully created at {VECTOR_DB_DIR}")
        else:
            print("Failed to create vector store, cannot perform queries.")


    #Creating the Document DB
    if vector_store_has_embeddings(SCRAPED_VECTOR_DB_DIR):
        print("Loading existing vector store...")
        scraped_vector_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)
    else:
        print("Primary-law vector store is missing or empty. Rebuilding it...")
        scraped_vector_db = create_scraped_vector_store(SCRAPED_VECTOR_DB_DIR)
        



if __name__ == "__main__":
    main()
