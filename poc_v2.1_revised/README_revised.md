# ⭐ Star: Massachusetts Housing Law RAG System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![LLM](https://img.shields.io/badge/LLM-OpenAI%20GPT--4o--mini-green)
![RAG](https://img.shields.io/badge/Architecture-RAG-orange)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## 📌 Overview

**Star** is a Retrieval-Augmented Generation (RAG) system designed to answer housing-related legal questions in Massachusetts with high accuracy and reliability.

It leverages:

* *Legal Tactics: Tenants’ Rights in Massachusetts* (PDF corpus)
* Scraped Massachusetts housing law data

The system is built to ensure:

* **Grounded responses** (evidence-backed answers)
* **High relevance** to user queries
* **Strong retrieval performance**

---

## 🎯 Objectives

The system is optimized to improve:

* **Grounded Score** — Ensuring answers are supported by retrieved documents
* **Answer Relevancy** — Ensuring responses directly address the query
* **Retrieval Recall** — Ensuring the correct information is retrieved

It supports multiple user roles:

* `general`
* `tenant`
* `landlord`

---

## 🧠 System Architecture

```
User Query
   ↓
Query Standardization
   ↓
Retriever (Dual Source)
   ├── Legal Tactics PDFs
   └── Scraped Law Database
   ↓
MMR Retrieval
   ↓
Global Reranker (Cross Encoder)
   ↓
Context Compression
   ↓
LLM (Role-Aware Prompting)
   ↓
Answer + Sources
   ↓
Evaluation (Grounded Score, Recall, Relevancy)
```

---

## 📂 Project Structure

```
.
├── app.py                       # Gradio UI
├── main.py                      # Builds vector databases
├── evaluate.py                  # Evaluation pipeline
├── config.py                    # Configuration settings
│
├── vector_store.py              # Retrieval, compression, generation
├── scraping_load.py             # Retrieval and reranking logic
├── text_processing.py           # Chunking logic
├── pdf_processing.py            # PDF extraction
│
├── prompt_engineering_user.py   # Prompt templates
├── openai_llm.py                # OpenAI integration
├── ollama_llm.py                # Optional local LLM backend
```

---

## ⚙️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add API Key

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
```

### 3. Configure Paths (`config.py`)

```python
DATA_DIR = "path_to_Legal-Tactics-Book.zip"
VECTOR_DB_DIR = "~/poc_chroma/chroma_db"
SCRAPED_VECTOR_DB_DIR = "~/poc_chroma/scraped_chroma_db"
```

---

## 🏗️ Build Vector Databases

```bash
python main.py
```

### What this step does:

* Extracts and processes PDFs
* Cleans and structures text
* Splits content into chunks
* Assigns role metadata
* Builds:

  * Legal Tactics vector database
  * Scraped law vector database

> ⚠️ Re-run this step if you modify:

* PDF processing
* Chunking logic
* Role assignments

---

## 🚀 Run the Application

```bash
python app.py
```

Then open the generated Gradio link in your browser.

---

## 📊 Evaluation

### Run Evaluation

```bash
python evaluate.py
```

---

## 📁 Outputs

### `evaluation_results.csv`

Per-question metrics:

* question
* answer
* contexts
* grounded_score
* retrieval_recall
* answer_relevancy

### `evaluation_summary.csv`

Aggregated metrics:

* grounded_score
* retrieval_recall
* answer_relevancy
* improvement suggestions

---

## 📊 Metrics Explained

### 🔹 Grounded Score

Measures how well the answer is supported by retrieved documents

* High → Evidence-based
* Low → Potential hallucination

### 🔹 Retrieval Recall

Measures whether the correct information was retrieved

### 🔹 Answer Relevancy

Measures how well the response matches the user’s query

---

## 🔧 Key Improvements

### 1. Retrieval Pipeline Upgrade (`scraping_load.py`)

* MMR retrieval
* Dual-source retrieval
* Cross-encoder reranking
* Threshold filtering
* Fallback mechanisms

**Result:** Improved evidence selection and grounded answers

---

### 2. Role-Aware Retrieval

* Supports `general`, `tenant`, and `landlord`
* Prioritizes role-specific context

**Result:** More relevant responses

---

### 3. Query-Aware Context Compression (`vector_store.py`)

* Extracts key sentences
* Preserves local context

**Result:** Reduced noise and improved grounding

---

### 4. Global Reranking

Model:

```
cross-encoder/ms-marco-MiniLM-L-6-v2
```

**Result:** Stronger prioritization of relevant evidence

---

### 5. Prompt Engineering

* Structured outputs:

  * Answer
  * Key Takeaways
  * Action Items
* Role-aware reasoning

---

### 6. Evaluation Pipeline Improvements (`evaluate.py`)

* Chapter-specific queries
* Strict grounding checks
* Hallucination penalties

---

### 7. Pipeline Enhancements (`main.py`)

* Cleaner PDF parsing
* Structured sections
* Improved chunking
* Role tagging

---

### 8. Configuration Optimization

```python
FINAL_CONTEXT_K = 4
RERANK_MIN_SCORE = 0.20
DOC_COMPRESSION_MAX_SENTENCES = 2
```

**Result:** Less noise, better answers

---

## 🔁 Workflow

### If you modify retrieval or prompting:

```bash
python evaluate.py
```

### If you modify PDFs or chunking:

```bash
python main.py
python evaluate.py
```

---

## 📈 Interpreting Results

| Metric        | Interpretation     |
| ------------- | ------------------ |
| Low Recall    | Weak retrieval     |
| Low Relevancy | Off-topic answers  |
| Low Grounded  | Hallucination risk |

---

## 🔍 Key Insight

> Increasing grounded score directly reduces hallucination.

---

## 🏁 Summary

This project implements a robust RAG pipeline featuring:

* Dual-source retrieval
* Cross-encoder reranking
* Role-aware reasoning
* Context compression
* Strict evaluation

**Outcome:**
More accurate, trustworthy, and contextually grounded legal answers for Massachusetts housing law.
