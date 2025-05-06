import json

# Load your scraped "final cleaned" file
with open('massachusetts_primary_laws_scraped_final.json', 'r', encoding='utf-8') as f:
    sections = json.load(f)

# Tiny function to isolate only the real law
def clean_final_text(section_text):
    lines = section_text.split("\n")
    real_text = []
    capture = False
    for line in lines:
        # Start capturing once a real section starts
        if line.strip().lower().startswith("section") and (":" in line or "." in line):
            capture = True
        if capture:
            real_text.append(line.strip())
    return "\n".join(real_text)

# Apply cleaning
perfect_sections = []

for sec in sections:
    final_text = clean_final_text(sec['section_text'])
    if final_text:  # Only save if we have non-empty cleaned text
        perfect_sections.append({
            "section_name": sec['section_name'],
            "section_url": sec['section_url'],
            "section_text": final_text
        })

# Save the perfectly cleaned JSON
with open('massachusetts_primary_laws_PERFECTION.json', 'w', encoding='utf-8') as f:
    json.dump(perfect_sections, f, indent=2, ensure_ascii=False)

print("✅ Saved PERFECT clean file as 'massachusetts_primary_laws_PERFECTION.json'")

