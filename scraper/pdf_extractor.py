import pdfplumber
import json
import os

INPUT_DIR = "data/raw/pdfs"
OUTPUT_FILE = "data/raw/pdf_pages.json"

def extract_pdf(path):
    pages = []
    try:
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    pages.append({
                        "url": f"file://{path}",
                        "title": os.path.basename(path),
                        "text": text.strip()
                    })
        print(f"  {os.path.basename(path):<50} → {len(pages)} pages extracted")
    except Exception as e:
        print(f"  [ERROR] {path} — {e}")
    return pages

def process():
    all_pages = []
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".pdf")]

    print(f"\n NUSTra PDF Extractor")
    print(f" Found {len(pdf_files)} PDFs\n")

    for pdf_file in pdf_files:
        path = os.path.join(INPUT_DIR, pdf_file)
        pages = extract_pdf(path)
        all_pages.extend(pages)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_pages, f, ensure_ascii=False, indent=2)

    print(f"\n Done!")
    print(f" Total pages extracted : {len(all_pages)}")
    print(f" Saved to              : {OUTPUT_FILE}")

if __name__ == "__main__":
    process()