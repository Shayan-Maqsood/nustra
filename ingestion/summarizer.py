import json
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE  = "data/raw/professors.json"
OUTPUT_FILE = "data/processed/professor_summaries.json"
os.makedirs("data/processed", exist_ok=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.1-8b-instant"


def build_prompt(professor):
    return f"""You are analyzing student reviews for a NUST professor.
Extract structured information and return ONLY valid JSON, nothing else.

Professor: {professor['title']}
School: {professor['school']}
Raw page text:
{professor['text'][:3000]}

Return this exact JSON structure:
{{
  "name": "professor full name",
  "school": "school abbreviation",
  "rating": "X.X/5",
  "total_reviews": number or 0,
  "one_line_summary": "one sentence summary of professor",
  "pros": ["pro1", "pro2"],
  "cons": ["con1", "con2"],
  "recommended_for": "which courses or students",
  "grading": "Easy/Moderate/Hard/Very Hard",
  "teaching_style": "brief description",
  "overall_verdict": "Recommended/Mixed/Not Recommended"
}}"""


def summarize_professor(professor):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": build_prompt(professor)}],
            temperature=0.1,
            max_tokens=500,
        )
        text = response.choices[0].message.content.strip()

        # Extract JSON from response
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start == -1 or end == 0:
            return None
        return json.loads(text[start:end])

    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def main():
    print("\n NUSTra Professor Summarizer (via Groq)")
    print("="*45)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        professors = json.load(f)

    print(f"  Loaded {len(professors)} professors")

    # Resume support — skip already processed
    summaries = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            summaries = json.load(f)
        print(f"  Resuming — {len(summaries)} already done")

    done_names = set(s.get("name", "").lower() for s in summaries)
    remaining  = [p for p in professors if p["slug"] not in done_names]

    print(f"  Remaining: {len(remaining)}\n")

    for i, prof in enumerate(remaining):
        print(f"  [{i+1}/{len(remaining)}] {prof['slug']}", end=" → ")
        summary = summarize_professor(prof)

        if summary:
            summary["source_url"] = prof["url"]
            summary["slug"]       = prof["slug"]
            summaries.append(summary)
            print(f"{summary.get('overall_verdict', '?')} | {summary.get('rating', '?')}")
        else:
            print("FAILED")

        # Save every 10 professors in case of crash
        if (i + 1) % 10 == 0:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(summaries, f, ensure_ascii=False, indent=2)
            print(f"  [Checkpoint saved — {len(summaries)} total]")

        time.sleep(0.3)  # stay within rate limits

    # Final save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print(f"\n Done!")
    print(f"  Summaries generated : {len(summaries)}")
    print(f"  Saved to            : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()