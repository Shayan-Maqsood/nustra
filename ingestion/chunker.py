import json
import os
import re
import sys

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

        if len(chunk_words) > 5:
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
        print(f"  [ERROR] No FAQ file found: {faq_path}. Please run faq_scraper first.")
        sys.exit(1)

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
        if len(text) < 20:
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