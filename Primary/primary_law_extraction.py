# Scrape Massachusetts General Laws (Primary Law Source)
import requests
from bs4 import BeautifulSoup
import time
import re

# Example chapters you want (you can add more from your list)
chapter_urls = [
    "https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter184",   # Real Property
    "https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter185C",  # Housing Court
    "https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186",   # Estates for Years and At Will
    "https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186A",  # Foreclosed Properties
    "https://malegislature.gov/Laws/GeneralLaws/PartIII/TitleIII/Chapter239", # Evictions (Summary Process)
    "https://malegislature.gov/Laws/GeneralLaws/PartII/TitleIII/Chapter209A",
    "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVII/Chapter121B",
    "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter59/Section12C", 
    "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter40T",
    "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVI/Chapter111",
    "https://malegislature.gov/Laws/GeneralLaws/PartIII/TitleIII/Chapter242",
    "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXX/Chapter139",
    "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXV/Chapter93A"
]

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

# Function to scrape a single chapter
def scrape_chapter(chapter_url):
    print(f"🔍 Scraping Chapter: {chapter_url}")
    chapter_response = requests.get(chapter_url, headers=headers)
    chapter_soup = BeautifulSoup(chapter_response.text, "html.parser")

    # Find all section links
    sections = chapter_soup.select("ul.generalLawsList li a")
    base_url = "https://malegislature.gov"

    chapter_data = []

    for section in sections:
        section_name = section.get_text(strip=True)
        section_href = section.get('href')
        full_section_url = base_url + section_href

        time.sleep(1)  # Be gentle

        section_response = requests.get(full_section_url, headers=headers)
        section_soup = BeautifulSoup(section_response.text, "html.parser")

        # Grab the section text
        content = section_soup.select_one(".law-text, .content, .section")
        if content:
            section_text = content.get_text(separator="\n", strip=True)
            # Clean redundant 'Go to General Law' and nav text
            section_text = re.sub(r'Go Directly to a General Law.*Print Page.*', '', section_text, flags=re.DOTALL)

            chapter_data.append({
                "section_name": section_name,
                "section_url": full_section_url,
                "section_text": section_text
            })
        else:
            print(f"⚠️ No content found for {section_name} at {full_section_url}")

    return chapter_data

# Scrape all chapters
all_law_data = []
for url in chapter_urls:
    chapter_sections = scrape_chapter(url)
    all_law_data.extend(chapter_sections)

print(f"✅ Scraped {len(all_law_data)} sections total.")

# Save all scraped sections
import json
with open("massachusetts_primary_laws_stored.json", "w", encoding="utf-8") as f:
    json.dump(all_law_data, f, indent=2, ensure_ascii=False)

print("✅ Saved all laws into 'massachusetts_primary_laws_stored.json'")
