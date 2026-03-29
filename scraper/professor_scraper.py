import requests
from bs4 import BeautifulSoup
import json
import os
import time

OUTPUT_FILE = "data/raw/professors.json"
os.makedirs("data/raw", exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def get_all_professor_urls():
    print("  Fetching sitemap...")
    r = requests.get("https://www.ratedeeznust.com/sitemap.xml", headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "xml")
    urls = [loc.text for loc in soup.find_all("loc") if "/professor/" in loc.text]
    print(f"  Found {len(urls)} professor URLs")
    return urls


def scrape_professor(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator="\n")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        clean = "\n".join(lines)

        # Extract name and school from URL slug
        slug = url.split("/professor/")[-1]
        parts = slug.split("-")
        school = parts[0].upper()

        return {
            "url": url,
            "slug": slug,
            "school": school,
            "title": soup.title.string.strip() if soup.title else slug,
            "text": clean
        }

    except Exception as e:
        print(f"    ERROR: {url} — {e}")
        return None


def main():
    print("\n RateDeezNUST Professor Scraper")
    print("="*45)

    urls = get_all_professor_urls()
    professors = []
    failed = 0

    for i, url in enumerate(urls):
        print(f"  [{i+1}/{len(urls)}] {url.split('/professor/')[-1]}")
        data = scrape_professor(url)
        if data and len(data["text"]) > 100:
            professors.append(data)
        else:
            failed += 1
        time.sleep(0.5)  # polite delay

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(professors, f, ensure_ascii=False, indent=2)

    print(f"\n Done!")
    print(f"  Scraped     : {len(professors)} professors")
    print(f"  Failed      : {failed}")
    print(f"  Saved to    : {OUTPUT_FILE}")
    print(f"  Size        : {os.path.getsize(OUTPUT_FILE)/1024:.1f} KB")


if __name__ == "__main__":
    main()