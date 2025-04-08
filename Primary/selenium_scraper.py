from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Load section URLs
with open('massachusetts_primary_laws.json', 'r', encoding='utf-8') as f:
    section_links = json.load(f)

# Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Scraping function
def scrape_section(section_url):
    driver = webdriver.Chrome(options=chrome_options)  # ← Move inside the function
    try:
        driver.get(section_url)
        content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".law-text, .section-content, .content"))
        )
        law_text = content.text.strip()
    except Exception as e:
        print(f"⚠️ Error scraping {section_url}: {e}")
        law_text = ""
    driver.quit()  # ← Close driver immediately after scraping
    return law_text

# Scrape all sections
scraped_sections = []

for section in section_links:
    section_name = section['section_name']
    section_url = section['section_url']

    print(f"🔍 Scraping {section_name} ...")
    time.sleep(1)  # To be polite

    full_text = scrape_section(section_url)

    if full_text:
        scraped_sections.append({
            "section_name": section_name,
            "section_url": section_url,
            "section_text": full_text
        })
    else:
        print(f"⚠️ No content found for {section_name}")

# Save final output
with open('massachusetts_primary_laws_fulltext.json', 'w', encoding='utf-8') as f:
    json.dump(scraped_sections, f, indent=2, ensure_ascii=False)

print("✅ Scraping finished. Saved to 'massachusetts_primary_laws_fulltext.json'.")

