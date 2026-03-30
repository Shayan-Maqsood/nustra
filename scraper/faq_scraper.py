"""
NUST FAQ Scraper
Scrapes all Q&A pairs from https://nust.edu.pk/faqs/ and its sub-category pages.
Uses cloudscraper to bypass Cloudflare protection.
"""

import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import time
import re

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)


def get_page(url, retries=3):
    """Fetch a page with retries."""
    for attempt in range(retries):
        try:
            response = scraper.get(url, timeout=15)
            if response.status_code == 200:
                return response.text
            print(f"  [WARN] Status {response.status_code} for {url}")
        except Exception as e:
            print(f"  [ERROR] Attempt {attempt+1}/{retries} for {url}: {e}")
        time.sleep(2)
    return None


def extract_faq_category_links(html):
    """Extract FAQ category links from the main FAQ page."""
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "faq-category" in href:
            if href.startswith("/"):
                href = "https://nust.edu.pk" + href
            if href not in links and "nust.edu.pk" in href:
                links.append(href)

    return links


def extract_faqs_from_page(html, url):
    """Extract Q&A pairs from a NUST FAQ page.
    
    The NUST site uses a Bootstrap accordion structure:
      .accordion#accordionExample > .card > .card-header > h2 > button (question)
      .accordion#accordionExample > .card > .collapse > .card-body (answer)
    """
    soup = BeautifulSoup(html, "html.parser")
    faqs = []

    # Get page title / category
    title_tag = soup.find("h1")
    if not title_tag:
        title_tag = soup.find("title")
    category = title_tag.get_text(strip=True) if title_tag else "General"
    category = category.replace(" | NUST", "").replace(" - NUST", "").strip()
    # Clean up category prefixes like "BSHND Admissions - FAQs"
    category = category.replace(" - FAQs", "").replace(" FAQs", "").strip()

    # ── Bootstrap accordion cards ─────────────────────────────
    cards = soup.select(".accordion .card, .accordion-item")
    for card in cards:
        # Question: inside button in card-header
        q_elem = card.select_one(".card-header button, .card-header h2, .accordion-header button")
        # Answer: inside card-body within collapse div
        a_elem = card.select_one(".collapse .card-body, .accordion-body, .collapse")

        if q_elem and a_elem:
            # Clean up the question text (remove accordion icons etc.)
            q_text = q_elem.get_text(strip=True)
            # Remove any leading/trailing special chars
            q_text = re.sub(r'^[\s\-\•\>\<]+', '', q_text).strip()

            # Get answer - preserve some structure
            a_text = a_elem.get_text(separator="\n", strip=True)
            # Clean up excessive whitespace
            a_text = re.sub(r'\n{3,}', '\n\n', a_text)
            a_text = re.sub(r'[ \t]{2,}', ' ', a_text)

            if q_text and a_text and len(q_text) > 5:
                faqs.append({
                    "question": q_text,
                    "answer": a_text,
                    "category": category,
                    "source": url
                })

    # ── Fallback: dt/dd definition lists ──────────────────────
    if not faqs:
        dts = soup.find_all("dt")
        for dt in dts:
            dd = dt.find_next_sibling("dd")
            if dd:
                q = dt.get_text(strip=True)
                a = dd.get_text(strip=True)
                if q and a:
                    faqs.append({"question": q, "answer": a, "category": category, "source": url})

    # ── Fallback: h3/h4 + p pairs (question-like headings) ───
    if not faqs:
        headings = soup.find_all(["h3", "h4"])
        for h in headings:
            text = h.get_text(strip=True)
            if "?" in text or text.lower().startswith(("what", "how", "when", "where", "who", "why", "is ", "are ", "can ", "do ", "does ")):
                answer_parts = []
                sibling = h.find_next_sibling()
                while sibling and sibling.name not in ["h3", "h4", "h2", "h1"]:
                    if sibling.name in ["p", "ul", "ol", "div"]:
                        answer_parts.append(sibling.get_text(strip=True))
                    sibling = sibling.find_next_sibling()
                if answer_parts:
                    a = " ".join(answer_parts)
                    faqs.append({"question": text, "answer": a, "category": category, "source": url})

    return faqs


def main():
    all_faqs = []
    visited = set()

    print("\n" + "=" * 50)
    print(" NUST FAQ Scraper")
    print("=" * 50)

    # ── Step 1: Scrape main FAQ page ──────────────────────────
    main_url = "https://nust.edu.pk/faqs/"
    print(f"\n[1] Fetching main FAQ page: {main_url}")

    html = get_page(main_url)
    if not html:
        print("  FATAL: Could not fetch main FAQ page!")
        return

    visited.add(main_url)
    print(f"  Page fetched ({len(html)} bytes)")

    # Extract FAQs from main page itself
    main_faqs = extract_faqs_from_page(html, main_url)
    if main_faqs:
        all_faqs.extend(main_faqs)
        print(f"  Found {len(main_faqs)} FAQs on main page")

    # ── Step 2: Find sub-category pages ───────────────────────
    category_links = extract_faq_category_links(html)
    print(f"\n[2] Found {len(category_links)} FAQ category links:")
    for link in category_links:
        print(f"    → {link}")

    # ── Step 3: Scrape each category page ─────────────────────
    for i, link in enumerate(category_links):
        if link in visited:
            continue
        visited.add(link)

        print(f"\n[3.{i+1}] Scraping: {link}")
        html = get_page(link)
        if not html:
            continue

        page_faqs = extract_faqs_from_page(html, link)
        if page_faqs:
            all_faqs.extend(page_faqs)
            print(f"  ✓ Found {len(page_faqs)} FAQs")
        else:
            print(f"  ✗ No FAQs found")

        time.sleep(1)  # polite delay

    # ── Step 4: Deduplicate ───────────────────────────────────
    seen = set()
    unique_faqs = []
    for faq in all_faqs:
        key = faq["question"].strip().lower()
        if key not in seen:
            seen.add(key)
            unique_faqs.append(faq)

    print(f"\n[4] Deduplication: {len(all_faqs)} → {len(unique_faqs)} unique FAQs")

    # ── Step 5: Save ──────────────────────────────────────────
    output_path = os.path.join(OUTPUT_DIR, "nust_faqs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unique_faqs, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 50}")
    print(f" Done!")
    print(f" Total FAQs   : {len(unique_faqs)}")
    print(f" Categories   : {len(set(f['category'] for f in unique_faqs))}")
    print(f" Saved to     : {output_path}")
    print(f" File size    : {os.path.getsize(output_path) / 1024:.1f} KB")
    print(f"{'=' * 50}\n")

    # Print summary by category
    categories = {}
    for faq in unique_faqs:
        cat = faq["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("FAQs by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    # Print first few for verification
    print("\n--- Sample FAQs ---")
    for faq in unique_faqs[:3]:
        print(f"\nQ: {faq['question'][:100]}")
        print(f"A: {faq['answer'][:150]}...")
        print(f"Category: {faq['category']}")


if __name__ == "__main__":
    main()
