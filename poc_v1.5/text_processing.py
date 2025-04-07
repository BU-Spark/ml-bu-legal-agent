from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_chunks_with_headers(markdown_sections, text_splitter):
    """Splits text while ensuring section headers remain in context."""
    all_chunks = []

    for section in markdown_sections:
        section_title = section.split("\n")[0]  # Extract the first line (header)
        chunks = text_splitter.split_text(section)

        for chunk in chunks:
            enriched_chunk = f"{section_title}\n\n{chunk}"  # Attach section header to each chunk
            all_chunks.append(enriched_chunk)

    return all_chunks