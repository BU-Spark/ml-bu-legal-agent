# Scraper with NEW driver for each section (safe method)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Load sections
with open('massachusetts_primary_laws_stored.json', 'r', encoding='utf-8') as f:
    section_links = json.load(f)

# Setup Selenium options (only options here, not driver)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Scrape one section with fresh Chrome driver
def scrape_clean_section(section_url):
    driver = webdriver.Chrome(options=chrome_options)  # create fresh driver inside the function
    try:
        driver.get(section_url)
        content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".law-text, .section-content, .content"))
        )
        full_text = content.text.strip()
        
        # Clean junk
        lines = full_text.split("\n")
        clean_lines = []
        for line in lines:
            if any(junk in line.lower() for junk in ["general laws", "skip to content", "part i", "part ii", "title", "chapter", "prev", "next", "print page", "search"]):
                continue
            clean_lines.append(line.strip())

        cleaned_text = "\n".join(clean_lines)
    except Exception as e:
        print(f"⚠️ Error scraping {section_url}: {e}")
        cleaned_text = ""
    driver.quit()  # close driver immediately after scraping
    return cleaned_text

# Scrape all sections
scraped_sections = []

for section in section_links:
    section_name = section['section_name']
    section_url = section['section_url']

    print(f"🔍 Scraping {section_name} ...")
    time.sleep(1)  # polite

    full_clean_text = scrape_clean_section(section_url)

    if full_clean_text:
        scraped_sections.append({
            "section_name": section_name,
            "section_url": section_url,
            "section_text": full_clean_text
        })
    else:
        print(f"⚠️ No real content found for {section_name}")

# Save final scraped output
with open('massachusetts_primary_laws_scraped_final.json', 'w', encoding='utf-8') as f:
    json.dump(scraped_sections, f, indent=2, ensure_ascii=False)

print("✅ Scraping finished successfully. Saved to 'massachusetts_primary_laws_scraped_final.json'.")
