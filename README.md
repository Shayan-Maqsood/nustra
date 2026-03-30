# NUSTra — NUST FAQ Retrieval Assistant

> A fully offline AI chatbot that answers questions about NUST using RAG (Retrieval-Augmented Generation) based exclusively on official FAQs. No internet required after setup.

---

## What is NUSTra?

NUSTra is a locally-running AI chatbot built specifically to help students and parents navigate NUST (National University of Sciences & Technology, Pakistan) through its official Frequently Asked Questions. It provides instant, grounded answers to queries regarding:

- Admissions, merit lists & entry test (NET) requirements
- Fee structures, installments & scholarships
- Eligibility criteria for various undergraduate programs (Engineering, Computing, Medical, etc.)
- Hostel facilities, transport, and campus life
- International & expatriate student admissions

---

## How it works
```
User Question
     │
     ▼
Embed query with all-MiniLM-L6-v2 (local, offline)
     │
     ▼
Semantic search across 430+ NUST FAQ chunks in FAISS (local)
     │
     ▼
Top 5 most relevant FAQ chunks retrieved
     │
     ▼
Qwen 2.5 3B generates grounded answer (local, offline)
     │
     ▼
Response streamed to Gradio UI
```

---

## Hardware Requirements

| Component | Minimum | Tested On |
|-----------|---------|-----------|
| RAM | 8 GB | 8 GB |
| CPU | Intel Core i5 (any gen) | i5 13th Gen |
| GPU | Not required | None |
| Storage | ~5 GB | ~5 GB |
| Internet | Only for initial setup | — |

---

## Knowledge Base

| Source | Content | Size |
|--------|---------|------|
| nust.edu.pk/faqs | Official Undergraduate Admissions FAQs | 430+ Questions |
| **Total** | **430+ searchable FAQ chunks** | **~35KB processed** |

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Git
- Ollama (https://ollama.com)

### 1. Install Ollama and pull model
```bash
ollama pull qwen2.5:3b
```

### 2. Clone the repository
```bash
git clone https://github.com/Shayan-Maqsood/nustra.git
cd nustra
```

### 3. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Launch NUSTra

**Windows — double click:**
```
run.bat
```

**Or via terminal:**
```bash
python app/chat.py
```

Open browser at: **http://127.0.0.1:7860**

---

## Project Structure
```
nustra/
├── app/
│   └── chat.py                    # Gradio chat UI & RAG orchestration
├── data/
│   ├── raw/                       # Scraped FAQ JSON data
│   ├── processed/                 # Refined FAQ chunks
│   └── chroma_db/                 # FAISS vector index & metadata
├── ingestion/
│   ├── chunker.py                 # FAQ text chunking pipeline
│   ├── embedder.py                # MiniLM embedding + FAISS indexing
│   └── summarizer.py              # Optional content summarization logic
├── rag/
│   ├── retriever.py               # FAISS semantic search logic
│   └── pipeline.py                # RAG loop + Qwen inference via Ollama
├── scraper/
│   └── faq_scraper.py             # Official NUST FAQ scraper
├── .env                           # Environment configuration
├── requirements.txt
├── run.bat                        # One-click Windows launcher
└── README.md
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Qwen 2.5 3B | Fast, accurate, fits in 8GB RAM |
| LLM Runtime | Ollama | CPU-optimized, zero config |
| Embeddings | all-MiniLM-L6-v2 | 80MB, fast CPU inference |
| Vector Store | FAISS | High performance, local-first |
| UI | Gradio | Instant streaming chat interface |
| Scraping | BeautifulSoup4 | Reliable FAQ parsing |

---

## Data Pipeline (one-time setup)

If you want to rebuild the FAQ knowledge base from scratch:
```bash
# 1. Scrape NUST FAQs
python scraper/faq_scraper.py

# 2. Chunk FAQ data
python ingestion/chunker.py

# 3. Embed and Index
python ingestion/embedder.py
```

---

## Sample Questions

- *"What is the merit for BS Computer Science?"*
- *"Are there any quota or reserved seats?"*
- *"Can Pre-Medical students apply for Engineering?"*
- *"What is the fee structure for MBBS at NSHS?"*
- *"Is there negative marking in the NUST Entry Test?"*
- *"What documents are required for admission?"*

---

## Built For

**NUST Hackathon — Automated Retrieval & Response Challenge**
Constraints: 8GB RAM · Core i5 · No GPU · No Internet at runtime

---

*Built with Python · Ollama · FAISS · Gradio · BeautifulSoup*