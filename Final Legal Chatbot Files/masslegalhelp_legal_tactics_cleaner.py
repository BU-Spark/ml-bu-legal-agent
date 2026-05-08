# legal_tactics_cleaner.py
# Cleans the raw scraped Legal Tactics JSON from legal_tactics_scraper.py
#
# Input:  legal_tactics_scraped_raw.json
# Output: legal_tactics_scraped_clean.json
#
# Run order: legal_tactics_scraper.py → legal_tactics_cleaner.py → legal_tactics_to_chroma.py

import json
import re


def clean_text(text: str) -> str:
    """Remove excessive whitespace, stray unicode, and normalize newlines."""
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)
    return text.strip()


def is_valid_section(section: dict) -> bool:
    """Return True if the section has enough usable content."""
    text = section.get("section_text", "")
    name = section.get("section_name", "")
    url  = section.get("section_url", "")

    if not text or not name or not url:
        return False

    if len(text) < 50:
        return False

    return True


# Load raw scraped data
with open("legal_tactics_scraped_raw.json", "r", encoding="utf-8") as f:
    raw_sections = json.load(f)

print(f"📥 Loaded {len(raw_sections)} raw sections")

# Clean and filter
clean_sections = []
skipped = 0

for section in raw_sections:
    if not is_valid_section(section):
        skipped += 1
        continue

    clean_sections.append({
        "section_name": section["section_name"].strip(),
        "section_url":  section["section_url"].strip(),
        "section_text": clean_text(section["section_text"])
    })

# Save cleaned output
with open("legal_tactics_scraped_clean.json", "w", encoding="utf-8") as f:
    json.dump(clean_sections, f, indent=2, ensure_ascii=False)

print(f"✅ Cleaning complete.")
print(f"   Kept:    {len(clean_sections)} sections")
print(f"   Skipped: {skipped} sections (too short or missing fields)")
print(f"   Saved to: legal_tactics_scraped_clean.json")
