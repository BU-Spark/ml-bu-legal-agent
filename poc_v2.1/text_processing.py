from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_chunks_with_headers(page_records, text_splitter):
    """Splits page records while keeping section headers in context."""
    all_chunks = []

    for record in page_records:
        metadata = dict(record.get("metadata", {}))
        content = record.get("content", "").strip()
        section_title = metadata.get("section_title")

        if not content:
            continue

        text = f"## {section_title}\n\n{content}" if section_title else content
        chunks = text_splitter.split_text(text)

        for chunk in chunks:
            all_chunks.append({
                "page_content": chunk,
                "metadata": metadata.copy(),
            })

    return all_chunks
