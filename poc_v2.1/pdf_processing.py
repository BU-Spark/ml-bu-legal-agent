import os
import zipfile
import pdfplumber
import re

def extract_zip(uploaded_zip_path, extract_to="../temp_pdfs"):
    """Extracts a zipped folder containing PDFs."""
    os.makedirs(extract_to, exist_ok=True)  # Ensure extraction folder exists

    with zipfile.ZipFile(uploaded_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    pdf_files = []
    for root, _, files in os.walk(extract_to):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))

    return pdf_files

def pdf_to_markdown_string(pdf_path):
    """Extracts page-aware content while preserving the current section header."""
    with pdfplumber.open(pdf_path) as pdf:
        current_section = None
        skipped_pages = 2  # Skip first two pages bc table of contents extends 
        page_records = []

        for page_num, page in enumerate(pdf.pages[skipped_pages:], start=skipped_pages + 1):
            text = page.extract_text()
            if not text:
                continue

            lines = [line.strip() for line in text.split("\n") if line.strip()]
            page_section = current_section
            page_lines = []

            for line in lines:
                if re.match(r"^\s*Chapter \d+:?", line) or re.match(r"^[A-Z][A-Z\s]+$", line.strip()):
                    current_section = line.strip()
                    page_section = current_section
                    continue

                page_lines.append(line.strip())

            page_text = "\n".join(page_lines).strip()
            if page_text:
                page_records.append({
                    "content": page_text,
                    "metadata": {
                        "source": os.path.basename(pdf_path),
                        "section_title": page_section,
                        "page_number": page_num,
                    },
                })

    return page_records

def determine_role(text):
    """Assigns a role based on detected keywords. Might need to do a bit more research 
    on keywords themselves to see which ones are the correct keywords to put in each list."""
    tenant_keywords = ["tenant rights", "rent control", "eviction protections", "lease termination"]
    landlord_keywords = ["landlord duties", "property maintenance", "rent collection", "eviction process"]

    if any(keyword in text.lower() for keyword in tenant_keywords):
        return "tenant"
    elif any(keyword in text.lower() for keyword in landlord_keywords):
        return "landlord"
    return "general"  # Default if no clear role is identified


def process_single_pdf(pdf_path):
    """Processes a single PDF into page-aware content records."""
    return pdf_to_markdown_string(pdf_path)
