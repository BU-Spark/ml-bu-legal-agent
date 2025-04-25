# PDF Document Processing and Semantic Search with Role Filtering

This codebase provides a pipeline for processing a collection of PDF documents within a ZIP archive, converting their content into searchable embeddings, and allowing you to query this data with a focus on specific roles (e.g., "tenant" or "landlord").

## Overview

The process involves the following key steps:

1.  **Loading Configuration:** Reads environment variables (specifically the OpenAI API key) from a `.env` file.
2.  **PDF Extraction:** Extracts PDF files from a provided ZIP archive.
3.  **Content Extraction and Structuring:** Reads the text content of each PDF, attempts to identify section headers, and formats the content in a markdown-like structure.
4.  **Role Determination:** Analyzes the text content of chunks to assign a potential role ("tenant", "landlord", or "general") based on the presence of predefined keywords.
5.  **Text Chunking:** Splits the structured text into smaller, overlapping chunks to optimize for embedding and search. Section headers are preserved within each chunk for better context.
6.  **Vector Store Creation:** Utilizes OpenAI embeddings to convert the text chunks into numerical vector representations and stores them in a Chroma vector database. This allows for efficient semantic search.
7.  **Querying the Vector Store:** Enables you to query the vector database with natural language questions. The search uses Maximum Marginal Relevance (MMR) to provide a diverse set of relevant results. You can also filter search results based on the determined role of the content.

## File Structure

The codebase is modularized into the following files:

* **`config.py`:**
    * Handles loading environment variables (like the OpenAI API key) from a `.env` file.
    * Defines project-level constants such as the directory for the Chroma vector database and a temporary directory for extracted PDFs.
* **`pdf_processing.py`:**
    * Contains functions for extracting PDF files from a ZIP archive (`extract_zip`).
    * Extracts text content from individual PDFs while attempting to preserve structure based on headings (`pdf_to_markdown_string`).
    * Assigns a role ("tenant", "landlord", or "general") to text based on keyword matching (`determine_role`).
    * Provides a function to process a single PDF into markdown sections (`process_single_pdf`).
* **`text_processing.py`:**
    * Includes a function (`create_chunks_with_headers`) to split markdown-formatted text into smaller chunks, ensuring that the original section headers are included with each chunk for context.
* **`vector_store.py`:**
    * Contains functions for creating a Chroma vector store from text chunks using OpenAI embeddings (`create_vector_store`).
    * Provides a function (`query_vector_store`) to search the vector store using Maximum Marginal Relevance (MMR) and allows filtering results by a specified role.
* **`main.py`:**
    * The main script that orchestrates the entire process.
    * Loads the API key.
    * Defines the path to the input ZIP file.
    * Calls functions to extract, process, and chunk the PDF documents.
    * Creates the Chroma vector store.
    * Demonstrates example queries for tenant-related and landlord-related information, filtering the results by their determined roles.

## Setup and Usage

### Prerequisites

* **Python 3.6+**
* **pip** (Python package installer)
* An **OpenAI API key**. You will need to create an account on the OpenAI platform to obtain this key.

### Installation

1.  Clone this repository (if you have it in one).
2.  Navigate to the project directory in your terminal.
3.  Install the required Python libraries using pip:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Create a `.env` file in the parent directory of your project (one level up from where `main.py` is located).
2.  Add your OpenAI API key to the `.env` file in the following format:

    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```

3.  (Optional) Modify the `DATA_DIR` in `config.py` to point to the data folder with the ZIP file containing your PDF documents, or ensure a file named `your_zip_path.zip` exists in the same directory as `main.py` (or provide the path directly in `main.py`).

### Running the Code

1.  Open your terminal and navigate to the project directory.
2.  Run the `main.py` script:

    ```bash
    python main.py
    ```

3.  The script will:
    * Process the PDFs from the specified ZIP file.
    * Create a Chroma vector database in a directory named `chroma_db` in your current working directory.
    * Print the total number of processed chunks and an example chunk with its metadata.
    * Perform example queries for tenant and landlord information, showing the top results.

## Key Concepts

* **Embeddings:** Numerical representations of text that capture their semantic meaning. OpenAI's API is used to generate these embeddings.
* **Vector Store:** A database that stores these embeddings, allowing for efficient similarity search. Chroma is used in this project.
* **Maximum Marginal Relevance (MMR):** A technique used in search to balance relevance to the query with the diversity of the returned results.
* **Role Filtering:** The ability to filter search results based on a determined role ("tenant", "landlord") associated with the text chunks. This relies on keyword-based classification.

## Potential Improvements and Future Work

* **More Robust Role Determination:** Implement more sophisticated methods for role classification, such as using machine learning models, to improve accuracy.
* **Dynamic ZIP File Path:** Allow the user to specify the ZIP file path as a command-line argument or through configuration.
* **Configuration Options:** Make chunk size, overlap, and other parameters configurable.
* **Error Handling:** Implement more comprehensive error handling throughout the codebase.
* **Persistence of Vector Store:** The current implementation removes the existing vector store each time it runs. Consider making persistence optional or the default behavior.
* **User Interface:** Develop a user interface (e.g., using Gradio as suggested by the initial `requirements.txt`) to interact with the system and perform custom queries.
* **Advanced Text Processing:** Explore more advanced techniques for text extraction and structuring.
* **Testing:** Add unit and integration tests to ensure the reliability of the codebase.

This README provides a comprehensive overview of the codebase, its functionality, setup instructions, and potential areas for improvement.