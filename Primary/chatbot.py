# ==============================================
# 1. Import Libraries
# ==============================================
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

import re

# ==============================================
# 2. Load Chroma VectorStore
# ==============================================
persist_directory = "massachusetts_laws_chroma_db"

# Reuse the same embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load the Chroma vectorstore
law_vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_model
)

print("✅ Chroma VectorStore loaded successfully.")

# ==============================================
# 3. Helper Function to Extract Chapter, Section
# ==============================================
def extract_chapter_section(url):
    """
    Given a URL like:
    https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter184/Section1
    it extracts ('184', '1')
    """
    match = re.search(r'Chapter(\d+[A-Z]*)/Section(\d+[A-Z]*)', url)
    if match:
        chapter = match.group(1)
        section = match.group(2)
        return chapter, section
    else:
        return None, None

# ==============================================
# 4. Ask a Question and Get Answer
# ==============================================
# def ask_question(query, k=2):
#     """
#     query: the question string
#     k: number of top documents to retrieve
#     """
#     # Search the VectorStore
#     docs = law_vectorstore.similarity_search(query, k=k)

#     if not docs:
#         return "Sorry, I couldn't find any relevant Massachusetts law section."

#     # Take the most relevant document
#     top_doc = docs[0]
#     section_text = top_doc.page_content
#     metadata = top_doc.metadata

#     # Extract Chapter and Section
#     section_url = metadata.get('section_url', '')
#     section_name = metadata.get('section_name', '')

#     chapter, section = extract_chapter_section(section_url)

#     if chapter and section:
#         citation = f"According to Massachusetts General Laws, Chapter {chapter}, Section {section}: {section_name}."
#     else:
#         citation = "According to Massachusetts General Laws."

#     # Return the answer
#     answer = f"{section_text}\n\n{citation}\nFull Law: {section_url}"
#     return answer

def ask_question(query, k=2):
    """
    query: the question string
    k: number of top documents to retrieve
    """
    # Search the VectorStore
    docs = law_vectorstore.similarity_search(query, k=k)

    if not docs:
        return "Sorry, I couldn't find any relevant Massachusetts law section."

    # Take the most relevant document
    top_doc = docs[0]
    section_text = top_doc.page_content
    metadata = top_doc.metadata

    # Extract URL and Section Name
    section_url = metadata.get('section_url', '')
    section_name = metadata.get('section_name', '')

    # Extract Chapter and Section Number from URL
    chapter, section = extract_chapter_section(section_url)

    # 🔥 Fix: Clean section_name (remove "Section X" prefix if present)
    clean_section_title = section_name
    import re
    match = re.match(r"Section\s*\d+[A-Z]?\s*(.*)", section_name, re.IGNORECASE)
    if match:
        clean_section_title = match.group(1).strip()

    # Format the citation properly
    if chapter and section:
        citation = f"According to Massachusetts General Laws, Chapter {chapter}, Section {section}: {clean_section_title}."
    else:
        citation = "According to Massachusetts General Laws."

    # Return the formatted answer
    answer = f"{section_text}\n\n{citation}\nFull Law: {section_url}"
    return answer


# ==============================================
# 5. Test It!
# ==============================================
if __name__ == "__main__":
    while True:
        user_query = input("\n🔍 Ask a legal question (or type 'exit' to quit):\n> ")
        if user_query.lower() == 'exit':
            break
        response = ask_question(user_query)
        print("\n📜 Answer:\n")
        print(response)
