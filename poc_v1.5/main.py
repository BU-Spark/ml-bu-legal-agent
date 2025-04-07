# Module imports
from config import load_api_key, VECTOR_DB_DIR, TEMP_PDF_DIR, DATA_DIR
from pdf_processing import extract_zip, process_single_pdf, determine_role
from text_processing import create_chunks_with_headers
from vector_store import create_vector_store, query_vector_store

# Library imports
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def load_and_process_pdfs(zip_path):
    """Processes a zipped folder of PDFs, preserves headers, and splits into smaller chunks for vector storage."""
    pdf_files = extract_zip(zip_path, extract_to=TEMP_PDF_DIR)
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for pdf in pdf_files:
        markdown_sections = process_single_pdf(pdf)
        enriched_chunks = create_chunks_with_headers(markdown_sections, text_splitter)
        for chunk in enriched_chunks:
            role = determine_role(chunk)
            all_chunks.append(Document(page_content=chunk, metadata={"source": os.path.basename(pdf), "role": role}))
    return all_chunks


def main():
    load_api_key()
    data_dir = DATA_DIR
    zip_file_path = data_dir + "/Legal-Tactics-Book.zip" 

    print("Processing PDFs into chunks...")
    document_chunks = load_and_process_pdfs(zip_file_path)
    print(f"Total chunks created: {len(document_chunks)}")
    
    # Tests
    if document_chunks:
        print(f"Example chunk:\n{document_chunks[0].page_content[:500]}")
        print(f"Metadata: {document_chunks[0].metadata}")

    print("Building the vector store...")
    vector_db = create_vector_store(document_chunks, VECTOR_DB_DIR)
    if vector_db:
        print(f"Vector store successfully created at {VECTOR_DB_DIR}")

        # Example queries
        tenant_query = "What rights do tenants have during eviction?"
        landlord_query = "What obligations do landlords have for maintenance?"

        tenant_results = query_vector_store(vector_db, tenant_query, role="tenant")
        landlord_results = query_vector_store(vector_db, landlord_query, role="landlord")

        print("\nTenant Response:")
        for result in tenant_results:
            print(result[:300])

        print("\nLandlord Response:")
        for result in landlord_results:
            print(result[:300])
    else:
        print("Failed to create vector store, cannot perform queries.")

if __name__ == "__main__":
    main()