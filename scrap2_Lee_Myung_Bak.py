import requests
from bs4 import BeautifulSoup
import json
import time
import os

# Helper function to save results to JSON
def save_to_json(results, output_file):
    """Save results list to JSON file"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved {len(results)} texts to {output_file}")

# File paths
input_file = "president_links_Lee_Myung_Bak.json"
output_file = "president_texts_Lee_Myung_Bak.json"

# Load URLs from scrap1 output
try:
    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)
except FileNotFoundError:
    print(f"{input_file} not found. Run scrap1_Lee_Myung_Bak.py first.")
    exit(1)

# Load existing results if file exists (resume capability)
results = []
processed_urls = set()

if os.path.exists(output_file):
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            results = json.load(f)
            processed_urls = {r.get("url", "") for r in results}
        print(f"📂 Loaded {len(results)} existing texts from {output_file}")
    except Exception as e:
        print(f"⚠️  Could not load existing file: {e}")
        results = []
        processed_urls = set()

total = len(articles)
print(f"Processing {total} articles for President Lee Myung-bak (이명박)...\n")

for idx, article in enumerate(articles, 1):
    url = article["url"]
    title = article["title"]
    
    # Skip if already processed
    if url in processed_urls:
        print(f"[{idx}/{total}] ⏭️  Skipping (already processed): {title}")
        continue
    
    print(f"[{idx}/{total}] Scraping: {title}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract content from td.content
        content_td = soup.select_one("td.content")
        
        paragraphs = []
        if content_td:
            text = content_td.get_text(separator="\n", strip=True)
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        
        # Extract date from the table (label "연설일자")
        date = ""
        table_rows = soup.select("table.board-view tbody tr")
        for row in table_rows:
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td and "연설일자" in th.get_text(strip=True):
                date = td.get_text(strip=True)
                break
        
        if paragraphs:
            results.append({
                "url": url,
                "title": title,
                "date": date,
                "paragraphs": paragraphs
            })
            processed_urls.add(url)
        else:
            print(f"  ⚠️  Warning: No content found for {url}")

        # Save every 20 texts
        if len(results) > 0 and len(results) % 20 == 0:
            save_to_json(results, output_file)

        time.sleep(1)

    except Exception as e:
        print(f"  ❌ Error on {title}: {e}")

print(f"\n✅ Total speeches scraped: {len(results)}/{total}")

# Final save
save_to_json(results, output_file)

print(f"File {output_file} created successfully!")
