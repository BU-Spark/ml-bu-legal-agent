# legal_tactics_scraper.py
# Scrapes all 18 Legal Tactics chapters from masslegalhelp.org
# Extracts each section with its direct anchor URL so users can click
# directly to the exact section — same approach as the MA primary laws scraper.
#
# Output: legal_tactics_scraped_raw.json
# Format: [{"section_name": "...", "section_url": "...#anchor", "section_text": "..."}]
#
# Run this file first, then run legal_tactics_cleaner.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# All 18 Legal Tactics chapter URLs on masslegalhelp.org
CHAPTER_URLS = [
    ("Chapter 1: Before You Move In",        "https://www.masslegalhelp.org/housing-apartments-shelter/tenants-rights/chapter-1-before-you-move-in"),
    ("Chapter 2: Tenant Screening",           "https://www.masslegalhelp.org/housing-apartments-shelter/tenants-rights/chapter-2-tenant-screening"),
    ("Chapter 3: Security Deposits",          "https://www.masslegalhelp.org/housing-apartments-shelter/security-deposits/chapter-3-security-deposits-and-last-months-rent"),
    ("Chapter 4: Kinds of Tenancies",         "https://www.masslegalhelp.org/housing-apartments-shelter/tenants-rights/chapter-4-kinds-tenancies"),
    ("Chapter 5: Rent",                       "https://www.masslegalhelp.org/housing-apartments-shelter/rent/chapter-5-rent"),
    ("Chapter 6: Utilities",                  "https://www.masslegalhelp.org/housing-apartments-shelter/utilities/chapter-6-utilities"),
    ("Chapter 7: Discrimination",             "https://www.masslegalhelp.org/housing-apartments-shelter/housing-discrimination/chapter-7-discrimination"),
    ("Chapter 8: Getting Repairs Made",       "https://www.masslegalhelp.org/housing-apartments-shelter/repairs/chapter-8-getting-repairs-made"),
    ("Chapter 9: Lead Poisoning",             "https://www.masslegalhelp.org/housing-apartments-shelter/lead-paint/chapter-9-lead-poisoning"),
    ("Chapter 10: Getting Organized",         "https://www.masslegalhelp.org/housing-apartments-shelter/tenants-rights/chapter-10-getting-organized"),
    ("Chapter 11: Moving Out",                "https://www.masslegalhelp.org/housing-apartments-shelter/tenants-rights/chapter-11-moving-out"),
    ("Chapter 12: Evictions",                 "https://www.masslegalhelp.org/housing-apartments-shelter/eviction/chapter-12-evictions"),
    ("Chapter 13: Taking Landlord to Court",  "https://www.masslegalhelp.org/housing-apartments-shelter/tenants-rights/chapter-13-taking-landlord-to-court"),
    ("Chapter 14: Using the Court System",    "https://www.masslegalhelp.org/housing-apartments-shelter/taking-your-landlord-court/chapter-14-using-court-system"),
    ("Chapter 15: Rooming Houses",            "https://www.masslegalhelp.org/housing-apartments-shelter/rooming-houses-mobile-homes-condos/chapter-15-rooming-houses"),
    ("Chapter 16: Mobile Homes",              "https://www.masslegalhelp.org/housing-apartments-shelter/rooming-houses-mobile-homes-condos/chapter-16-mobile-homes"),
    ("Chapter 17: Condominium Control",       "https://www.masslegalhelp.org/housing-apartments-shelter/rooming-houses-mobile-homes-condos/chapter-17-condominium-control"),
    ("Chapter 18: Tenants and Foreclosure",   "https://www.masslegalhelp.org/housing-apartments-shelter/tenants-rights/chapter-18-tenants-and-foreclosure"),
]

# Setup Selenium (acts like a real browser — avoids 403 blocks)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def scrape_chapter_sections(chapter_name, chapter_url):
    """
    Visits a Legal Tactics chapter page and extracts each section
    with its heading, text, and anchor URL.
    """
    driver = webdriver.Chrome(options=chrome_options)
    sections = []

    try:
        driver.get(chapter_url)
        time.sleep(3)  # wait for page to fully load

        # Find all section headings (h2, h3) that have an id attribute
        headings = driver.find_elements(By.CSS_SELECTOR, "h2[id], h3[id], h4[id]")

        if not headings:
            # Fallback: scrape full page as one section
            print(f"  ⚠️ No anchor headings found — scraping full page for {chapter_name}")
            try:
                body = driver.find_element(By.CSS_SELECTOR, "main")
            except:
                body = driver.find_element(By.TAG_NAME, "body")
            sections.append({
                "section_name": chapter_name,
                "section_url": chapter_url,
                "section_text": body.text.strip()
            })
        else:
            print(f"  ✅ Found {len(headings)} headings in {chapter_name}")
            for heading in headings:
                heading_id = heading.get_attribute("id")
                heading_text = heading.text.strip()
                if not heading_text or not heading_id:
                    continue

                anchor_url = f"{chapter_url}#{heading_id}"
                section_name = f"{chapter_name} — {heading_text}"

                # Try to get text from siblings first
                section_text = driver.execute_script("""
                    var heading = arguments[0];
                    var text = heading.textContent + '\\n';
                    var sibling = heading.nextElementSibling;
                    while (sibling && !['H2','H3','H4'].includes(sibling.tagName)) {
                        text += (sibling.innerText || sibling.textContent) + '\\n';
                        sibling = sibling.nextElementSibling;
                    }
                    return text.trim();
                """, heading)

                # If siblings gave nothing, try the parent container
                if not section_text or len(section_text) < 50:
                    section_text = driver.execute_script("""
                        var heading = arguments[0];
                        var parent = heading.parentElement;
                        return parent ? (parent.innerText || parent.textContent || '').trim() : '';
                    """, heading)

                if section_text and len(section_text) >= 50:
                    sections.append({
                        "section_name": section_name,
                        "section_url": anchor_url,
                        "section_text": section_text
                    })

            # If all headings gave empty content, fall back to full page
            if not sections:
                print(f"  ⚠️ Headings found but all empty — falling back to full page for {chapter_name}")
                try:
                    body = driver.find_element(By.CSS_SELECTOR, "main")
                except:
                    body = driver.find_element(By.TAG_NAME, "body")
                text = body.text.strip()
                if text:
                    sections.append({
                        "section_name": chapter_name,
                        "section_url": chapter_url,
                        "section_text": text
                    })

    except Exception as e:
        print(f"  ❌ Error scraping {chapter_url}: {e}")
    finally:
        driver.quit()

    return sections


# Main scraping loop
all_sections = []

for chapter_name, chapter_url in CHAPTER_URLS:
    print(f"🔍 Scraping: {chapter_name}")
    sections = scrape_chapter_sections(chapter_name, chapter_url)
    all_sections.extend(sections)
    print(f"  → {len(sections)} sections collected")
    time.sleep(2)  # polite delay between chapters

# Save raw output
with open("legal_tactics_scraped_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_sections, f, indent=2, ensure_ascii=False)

print(f"\n✅ Scraping complete. {len(all_sections)} total sections saved to legal_tactics_scraped_raw.json")
