# NUSTra — NUST Retrieval Assistant

> A fully offline AI chatbot that answers questions about NUST using RAG (Retrieval-Augmented Generation). No internet required after setup.

---

## What is NUSTra?

NUSTra is a locally-running AI chatbot built specifically for NUST (National University of Sciences & Technology, Pakistan). It answers questions about:

- Admissions, merit lists & entry test requirements
- Programs & degree requirements across all schools
- Fee structures & scholarships
- Hostel & campus life
- All NUST schools (SEECS, SMME, CEME, MCS, NICE, S3H, and more)
- **1000+ NUST professor ratings & student reviews**

---

## How it works
```
User Question
     │
     ▼
Embed query with MiniLM (local, offline)
     │
     ▼
Semantic search across 2500+ NUST chunks in FAISS (local)
     │
     ▼
Top 2 most relevant chunks retrieved
     │
     ▼
Qwen 2.5 3B generates grounded answer (local, offline)
     │
     ▼
Response streamed to browser UI
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
| nust.edu.pk + school sites | Programs, admissions, campus life | 171 pages |
| NUST PDFs | Prospectus, handbooks, hostel rules | Multiple PDFs |
| 1000+ professor ratings & reviews | 1000 professors |
| **Total** | **2500+ searchable chunks** | **~5MB indexed** |

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
│   └── chat.py                    # Gradio chat UI
├── data/
│   ├── raw/                       # Scraped pages + PDFs + professor data
│   ├── processed/                 # Chunks + professor summaries
│   └── chroma_db/                 # FAISS vector index (2500+ vectors)
├── ingestion/
│   ├── chunker.py                 # Text chunking pipeline
│   ├── embedder.py                # MiniLM embedding + FAISS indexing
│   └── summarizer.py              # Groq-powered professor summary generator
├── rag/
│   ├── retriever.py               # FAISS semantic search
│   └── pipeline.py                # RAG loop + Qwen inference
├── scraper/
│   ├── web_scraper.py             # NUST website crawler (171 pages)
│   ├── pdf_extractor.py           # PDF text extraction
│   └── professor_scraper.py       # RateDeezNUST scraper (1000 professors)
├── .env                           # API keys (not committed)
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
| Vector Store | FAISS | No compiler needed, production-grade |
| UI | Gradio 6 | Instant streaming chat interface |
| Scraping | BeautifulSoup4 | Reliable HTML parsing |
| PDF Parsing | pdfplumber | Accurate text extraction |
| Prof Summaries | Groq API (one-time) | Fast batch summarization during data prep |

---

## Data Pipeline (one-time setup)

If you want to rebuild the knowledge base from scratch:
```bash
# 1. Scrape NUST website
python scraper/web_scraper.py

# 2. Extract PDFs (place PDFs in data/raw/pdfs/ first)
python scraper/pdf_extractor.py

# 3. Scrape professor ratings
python scraper/professor_scraper.py

# 4. Generate professor summaries (requires GROQ_API_KEY in .env)
python ingestion/summarizer.py

# 5. Chunk all data
python ingestion/chunker.py

# 6. Embed and index
python ingestion/embedder.py
```

---

## Sample Questions

- *"What is the merit for SEECS Computer Science?"*
- *"How much is the fee for BS programs at NUST?"*
- *"Tell me about NUST hostel facilities"*
- *"What programs does SMME offer?"*
- *"How is Dr. Jaudat Mamoon as a professor?"*
- *"Which SEECS professors are recommended for FOCP?"*

---

## Built For

**NUST Hackathon — Individual Challenge, Live Finals**
Constraints: 8GB RAM · Core i5 · No GPU · No Internet at runtime

---

*Built with Python · Ollama · FAISS · Gradio · BeautifulSoup · Groq*