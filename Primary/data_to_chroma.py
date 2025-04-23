# # ================================
# # 1. Import Libraries
# # ================================
# import json
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.schema import Document
# import os

# # ================================
# # 2. Load Your Perfectly Cleaned Laws
# # ================================
# with open('massachusetts_primary_laws_PERFECTION.json', 'r', encoding='utf-8') as f:
#     sections = json.load(f)

# # ================================
# # 3. Setup HuggingFace Embedding Model
# # ================================
# embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# # ================================
# # 4. Prepare Documents for Chroma
# # ================================
# documents = [
#     Document(
#         page_content=section['section_text'],
#         metadata={
#             "section_name": section['section_name'],
#             "section_url": section['section_url'],
#             "source": "Massachusetts General Laws"
#         }
#     )
#     for section in sections
# ]

# # ================================
# # 5. Define Storage Location
# # ================================
# persist_directory = "massachusetts_laws_chroma_db"

# # Remove old DB if it exists (optional safety)
# if os.path.exists(persist_directory):
#     import shutil
#     shutil.rmtree(persist_directory)

# # ================================
# # 6. Create Chroma VectorStore
# # ================================
# law_vectorstore = Chroma.from_documents(
#     documents=documents,
#     embedding=embedding_model,
#     persist_directory=persist_directory
# )

# # Save (persist) database
# law_vectorstore.persist()

# print(f"✅ Successfully embedded and saved into '{persist_directory}' folder.")

# ================================
# 1. Import Libraries
# ================================
import json
import os
import shutil
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# ================================
# 2. Load Your Perfectly Cleaned Laws
# ================================
with open('massachusetts_primary_laws_PERFECTION.json', 'r', encoding='utf-8') as f:
    sections = json.load(f)

# ================================
# 3. Setup HuggingFace Embedding Model
# ================================
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ================================
# 4. Prepare Documents for Chroma
# ================================
documents = [
    Document(
        page_content=section['section_text'],
        metadata={
            "section_name": section['section_name'],
            "section_url": section['section_url'],
            "source": "Massachusetts General Laws"
        }
    )
    for section in sections
]

# ================================
# 5. Define Storage Location
# ================================
persist_directory = "massachusetts_laws_chroma_db"

# Remove old DB if it exists (optional safety)
if os.path.exists(persist_directory):
    shutil.rmtree(persist_directory)

# ================================
# 6. Create Chroma VectorStore
# ================================
law_vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    persist_directory=persist_directory
)

law_vectorstore.persist()
print(f"✅ Successfully embedded and saved into '{persist_directory}' folder.")

