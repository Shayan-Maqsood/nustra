import requests
from bs4 import BeautifulSoup
import time
import json
import os
from urllib.parse import urljoin, urlparse

# ── Output folder ──────────────────────────────────────────────
OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── All target URLs ────────────────────────────────────────────
SEED_URLS = [
    # Main
    "https://nust.edu.pk",
    "https://nust.edu.pk/about/",
    "https://nust.edu.pk/academics/",
    "https://nust.edu.pk/admissions/",
    "https://nust.edu.pk/research/",
    "https://nust.edu.pk/campus-life/",
    "https://nust.edu.pk/fee-structure/",
    "https://nust.edu.pk/scholarships/",
    "https://nust.edu.pk/hostels/",
    "https://nust.edu.pk/merit-lists/",

    # Schools
    "https://seecs.nust.edu.pk",
    "https://smme.nust.edu.pk",
    "https://ceme.nust.edu.pk",
    "https://mcs.nust.edu.pk",
    "https://nice.nust.edu.pk",
    "https://s3h.nust.edu.pk",
    "https://sada.nust.edu.pk",
    "https://asab.nust.edu.pk",
    "https://sns.nust.edu.pk",
    "https://pnec.nust.edu.pk",
    "https://iese.nust.edu.pk",
    "https://nbm.nust.edu.pk",
    "https://scme.nust.edu.pk",
    "https://rimms.nust.edu.pk",
    "https://igis.nust.edu.pk",
]

# ── Only stay on nust.edu.pk domains ──────────────────────────
ALLOWED_DOMAINS = [
    "nust.edu.pk",
    "seecs.nust.edu.pk",
    "smme.nust.edu.pk",
    "ceme.nust.edu.pk",
    "mcs.nust.edu.pk",
    "nice.nust.edu.pk",
    "s3h.nust.edu.pk",
    "sada.nust.edu.pk",
    "asab.nust.edu.pk",
    "sns.nust.edu.pk",
    "pnec.nust.edu.pk",
    "iese.nust.edu.pk",
    "nbm.nust.edu.pk",
    "scme.nust.edu.pk",
    "rimms.nust.edu.pk",
    "igis.nust.edu.pk",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

# ── Skip these file types ──────────────────────────────────────
SKIP_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".doc", ".docx", ".mp4", ".mp3"}

visited = set()
scraped_pages = []


def is_allowed(url):
    parsed = urlparse(url)
    return any(parsed.netloc.endswith(domain) for domain in ALLOWED_DOMAINS)


def should_skip(url):
    parsed = urlparse(url)
    _, ext = os.path.splitext(parsed.path)
    return ext.lower() in SKIP_EXTENSIONS


def extract_text(soup):
    # Remove nav, footer, scripts, styles
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    # Clean up blank lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def scrape_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"  [SKIP] {url} — status {response.status_code}")
            return None, []

        soup = BeautifulSoup(response.text, "html.parser")
        text = extract_text(soup)
        title = soup.title.string.strip() if soup.title else url

        # Collect child links
        links = []
        for a in soup.find_all("a", href=True):
            full_url = urljoin(url, a["href"])
            full_url = full_url.split("#")[0]  # strip anchors
            if (
                full_url not in visited
                and is_allowed(full_url)
                and not should_skip(full_url)
                and full_url.startswith("http")
            ):
                links.append(full_url)

        return {"url": url, "title": title, "text": text}, links

    except Exception as e:
        print(f"  [ERROR] {url} — {e}")
        return None, []


def crawl(max_pages=300):
    queue = list(SEED_URLS)

    print(f"\n NUSTra Web Scraper Starting")
    print(f" Target: up to {max_pages} pages\n")

    while queue and len(scraped_pages) < max_pages:
        url = queue.pop(0)

        if url in visited:
            continue
        visited.add(url)

        print(f"[{len(scraped_pages)+1}/{max_pages}] Scraping: {url}")

        page_data, new_links = scrape_page(url)

        if page_data and len(page_data["text"]) > 100:
            scraped_pages.append(page_data)
            queue.extend([l for l in new_links if l not in visited])

        time.sleep(1)  # polite delay — 1 second between requests

    print(f"\n Done! Scraped {len(scraped_pages)} pages.")


def save_results():
    output_path = os.path.join(OUTPUT_DIR, "scraped_pages.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scraped_pages, f, ensure_ascii=False, indent=2)
    print(f" Saved to {output_path}")
    print(f" Total pages: {len(scraped_pages)}")
    print(f" Approx size: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == "__main__":
    crawl(max_pages=300)
    save_results()