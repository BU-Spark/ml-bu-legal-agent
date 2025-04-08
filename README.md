# Web Scraping and Citation to Primary Source

This branch contains code which builds a Retrieval-Augmented Generation (RAG) system over the **Massachusetts General Laws** related to housing, tenant rights, and eviction.

✅ **Primary Source Only**  
✅ **No Books or Secondary Sources**  
✅ **Directly from: [malegislature.gov](https://malegislature.gov/Laws/GeneralLaws)**

---

## 📋 Branch Structure

| File/Folder | Purpose |
|:---|:---|
| `primary_law_extraction.py` | (Optional) Extracts list of law Section URLs |
| `final_scrapper.py` | Scrapes the full text of each law Section using Selenium |
| `final_cleaner.py` | Cleans the scraped data, removing extra website junk |
| `massachusetts_primary_laws_PERFECTION.json` | Final clean primary source dataset |
| `data_to_chroma.py` | Embeds the laws into a Chroma VectorStore |
| `massachusetts_laws_chroma_db/` | Folder storing the vector database |
| `chatbot.py` | Chatbot that retrieves real laws based on user questions |

---

## 🚀 How to Run the Code

### 1. Install Dependencies

```bash
pip install selenium
pip install langchain
pip install langchain-community
pip install langchain-core
pip install chromadb
pip install sentence-transformers
```

---

### 2. Scrape and Clean Data (Optional)

If needed:

```bash
python final_scrapper.py
python final_cleaner.py
```

Otherwise, use the provided `massachusetts_primary_laws_PERFECTION.json`.

---

### 3. Embed the Data into Chroma

```bash
python data_to_chroma.py
```

This creates a local database folder: `massachusetts_laws_chroma_db/`.

---

### 4. Run the Chatbot

```bash
python chatbot.py
```

Ask legal questions like:

> "I did not agree to a rental increase by the landlord, can I be evicted?"

and the chatbot will retrieve real Massachusetts laws with citations like:

> "According to Massachusetts General Laws, Chapter 186, Section 15F: Residential leases or rental agreements restricting litigation or landlord liability; ouster of tenant; remedies."

> "Full Law: https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter186/Section15F"

---

## 📚 Notes

- **Primary Sources Only**: Laws were directly scraped from [malegislature.gov](https://malegislature.gov/Laws/GeneralLaws), the official Massachusetts Legislature website and will cite the same like the client wanted.
- **No Secondary Sources** (e.g., no legal textbooks, no summaries).
- **Proper Citations**: Every answer cites the Chapter, Section, and Title.
- **Expandable**: Can add any number of URLs from the website (for example, right now the chapters which contain housing and tenant related issues are only scraped, can be extended to any topics, the entire website)

---

## 🔥 Upcoming Steps

- Integrate with other code

