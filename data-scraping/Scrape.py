from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Base URL for Chapter 239
base_url = "https://malegislature.gov/Laws/GeneralLaws/PartIII/TitleIII/Chapter239"

# Configure Selenium WebDriver (Headless Mode)
options = Options()
options.add_argument("--headless")  # Run without opening a browser window
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Open the main page
driver.get(base_url)
time.sleep(5)  # Allow JavaScript to load

# Wait for the page to fully load sections
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "generalLawsList"))
)

# Parse the page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Find all section links under 'generalLawsList'
section_links = soup.select("ul.generalLawsList li a")

# Dictionary to store scraped data
scraped_data = {}

def scrape_section(url, section_name, visited_links):
    """
    Recursively scrapes a given section URL, including any internal links within the section.
    """
    if url in visited_links:
        return  # Prevent duplicate scraping
    visited_links.add(url)

    print(f"🔍 Scraping {section_name}... ({url})")
    driver.get(url)
    time.sleep(5)  # Allow JavaScript to load

    # Wait for law text to appear
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".law-text, .content, .section"))
        )
    except Exception as e:
        print(f"⚠️ Timeout waiting for content in {section_name}: {e}")
        return

    # Parse section content
    section_soup = BeautifulSoup(driver.page_source, "html.parser")
    content_div = section_soup.select_one(".law-text, .content, .section")

    if content_div:
        section_text = content_div.get_text(separator="\n", strip=True)
        scraped_data[section_name] = section_text
    else:
        print(f"⚠️ No law text found for {section_name}")

    # Find internal links within this section (to follow and scrape more data)
    internal_links = section_soup.select("a[href^='/Laws/GeneralLaws/PartIII/TitleIII/Chapter239/Section']")
    for link in internal_links:
        sub_url = "https://malegislature.gov" + link["href"]
        sub_section_name = link.get_text(strip=True)
        scrape_section(sub_url, sub_section_name, visited_links)  # Recursively scrape

# Track visited links to avoid duplicates
visited_links = set()

# Scrape all primary section links
if section_links:
    for link in section_links:
        section_url = "https://malegislature.gov" + link["href"]
        section_name = link.get_text(strip=True)
        scrape_section(section_url, section_name, visited_links)
else:
    print("⚠️ No section links found! Website structure may have changed.")

# Close Selenium WebDriver
driver.quit()

# Save Data to Text File
if scraped_data:
    with open("chapter_239_evictions_full.txt", "w", encoding="utf-8") as file:
        for section, text in scraped_data.items():
            file.write(f"{section}\n{'='*80}\n{text}\n\n")
    print("✅ Scraping completed. Data saved to 'chapter_239_evictions_full.txt'.")
else:
    print("⚠️ No data extracted. Check website structure.")
