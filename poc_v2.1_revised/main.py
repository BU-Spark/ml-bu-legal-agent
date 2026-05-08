from config import (
    load_api_key,
    VECTOR_DB_DIR,
    TEMP_PDF_DIR,
    DATA_DIR,
    SCRAPED_VECTOR_DB_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from pdf_processing import extract_zip, process_single_pdf, determine_role
from text_processing import create_chunks_with_headers
from vector_store import create_vector_store, load_vector_store
from data_to_chroma_function import create_scraped_vector_store

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def load_and_process_pdfs(zip_path):
    pdf_files = extract_zip(zip_path, extract_to=TEMP_PDF_DIR)
    all_chunks = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n## ",
            "\n\n",
            "\n- ",
            "\n• ",
            "\n",
            ". ",
            " "
        ],
    )

    for pdf in pdf_files:
        markdown_sections = process_single_pdf(pdf)
        enriched_chunks = create_chunks_with_headers(markdown_sections, text_splitter)

        for chunk in enriched_chunks:
            role = determine_role(chunk)
            all_chunks.append(
                Document(
                    page_content=chunk,
                    metadata={"source": os.path.basename(pdf), "role": role}
                )
            )
    return all_chunks

def main():
    load_api_key()
    zip_file_path = DATA_DIR

    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        print("Loading existing vector store...")
        vector_db = load_vector_store(VECTOR_DB_DIR)
    else:
        print("Processing PDFs and building the vector store...")
        document_chunks = load_and_process_pdfs(zip_file_path)
        print(f"Total chunks created: {len(document_chunks)}")
        vector_db = create_vector_store(document_chunks, VECTOR_DB_DIR)

    if os.path.exists(SCRAPED_VECTOR_DB_DIR) and os.listdir(SCRAPED_VECTOR_DB_DIR):
        print("Loading existing scraped vector store...")
        scraped_vector_db = load_vector_store(SCRAPED_VECTOR_DB_DIR)
    else:
        print("Processing scraped law data and building the vector store...")
        scraped_vector_db = create_scraped_vector_store(SCRAPED_VECTOR_DB_DIR)

if __name__ == "__main__":
    main()