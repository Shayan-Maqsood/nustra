import json
import os
import re

WEB_FILE   = "data/raw/scraped_pages.json"
PDF_FILE   = "data/raw/pdf_pages.json"
OUTPUT_FILE = "data/processed/chunks.json"
os.makedirs("data/processed", exist_ok=True)

CHUNK_SIZE    = 400   # words per chunk
CHUNK_OVERLAP = 80    # words overlap between chunks


def clean_text(text):
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()


def split_into_chunks(text, url, title):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + CHUNK_SIZE
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        if len(chunk_words) > 50:
            chunks.append({
                "text": chunk_text,
                "source": url,
                "title": title,
                "chunk_index": len(chunks)
            })

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def load_pages():
    pages = []

    # Load web scraped pages
    if os.path.exists(WEB_FILE):
        with open(WEB_FILE, "r", encoding="utf-8") as f:
            web_pages = json.load(f)
        pages.extend(web_pages)
        print(f"  Web pages loaded  : {len(web_pages)}")
    else:
        print(f"  [WARN] Web file not found: {WEB_FILE}")

    # Load PDF extracted pages
    if os.path.exists(PDF_FILE):
        with open(PDF_FILE, "r", encoding="utf-8") as f:
            pdf_pages = json.load(f)
        pages.extend(pdf_pages)
        print(f"  PDF pages loaded  : {len(pdf_pages)}")
    else:
        print(f"  [INFO] No PDF file found yet: {PDF_FILE} — skipping")

    # Load professor summaries
    prof_summary_path = "data/processed/professor_summaries.json"
    if os.path.exists(prof_summary_path):
        with open(prof_summary_path, "r", encoding="utf-8") as f:
            summaries = json.load(f)
        prof_pages = []
        for s in summaries:
            text = f"""Professor: {s.get('name', '')}
                    School: {s.get('school', '')}
                    Rating: {s.get('rating', '')} ({s.get('total_reviews', 0)} reviews)
                    Summary: {s.get('one_line_summary', '')}
                    Pros: {', '.join(s.get('pros', []))}
                    Cons: {', '.join(s.get('cons', []))}
                    Recommended for: {s.get('recommended_for', '')}
                    Grading: {s.get('grading', '')}
                    Teaching style: {s.get('teaching_style', '')}
                    Verdict: {s.get('overall_verdict', '')}"""
            prof_pages.append({
                "url": s.get("source_url", ""),
                "title": f"Professor Review: {s.get('name', '')} ({s.get('school', '')})",
                "text": text
            })
        pages.extend(prof_pages)
        print(f"  Professor summaries : {len(prof_pages)}")
    else:
        print(f"  [INFO] No professor summaries found yet")

    # Load FAQ data
    faq_path = "data/raw/nust_faqs.json"
    if os.path.exists(faq_path):
        with open(faq_path, "r", encoding="utf-8") as f:
            faq_data = json.load(f)
        faq_pages = []
        for faq in faq_data:
            text = f"""FAQ Category: {faq.get('category', 'General')}
Question: {faq.get('question', '')}
Answer: {faq.get('answer', '')}"""
            faq_pages.append({
                "url": faq.get("source", "https://nust.edu.pk/faqs/"),
                "title": f"NUST FAQ: {faq.get('question', '')[:80]}",
                "text": text
            })
        pages.extend(faq_pages)
        print(f"  FAQ entries loaded : {len(faq_pages)}")
    else:
        print(f"  [INFO] No FAQ file found yet: {faq_path}")

    return pages


def process():
    print(f"\n NUSTra Chunker")
    print(f" Loading data sources...\n")

    pages = load_pages()

    print(f"\n Total pages      : {len(pages)}")
    print(f" Chunking now...\n")

    all_chunks = []

    for page in pages:
        text = clean_text(page["text"])
        if len(text) < 100:
            continue

        chunks = split_into_chunks(text, page["url"], page["title"])
        all_chunks.extend(chunks)
        print(f"  {page['title'][:60]:<60} → {len(chunks)} chunks")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n Done!")
    print(f" Total chunks : {len(all_chunks)}")
    print(f" Saved to     : {OUTPUT_FILE}")
    print(f" Approx size  : {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")


if __name__ == "__main__":
    process()