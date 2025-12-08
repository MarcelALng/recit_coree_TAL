import requests
from bs4 import BeautifulSoup
import json
import time

try:
    with open("president_links_Lee_Seung_Man.json", "r", encoding="utf-8") as f:
        articles = json.load(f)
except FileNotFoundError:
    print("president_links_Lee_Seung_Man.json not found. Run scrap1_Lee_Seung_Man.py first.")
    articles = []

results = []
total = len(articles)

for idx, article in enumerate(articles, 1):
    url = article["url"]
    title = article["title"]
    print(f"[{idx}/{total}] Scraping: {title}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Selectors identified:
        # Content: table.board-view > tbody > tr > td.content
        
        content_td = soup.select_one("td.content")
        
        paragraphs = []
        if content_td:
            # Get text, preserving some structure if possible, but mostly just text
            # The content seems to use <br> tags for separation
            text = content_td.get_text(separator="\n", strip=True)
            # Split by newlines to get paragraphs
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        
        if paragraphs:
            results.append({
                "title": title,
                "paragraphs": paragraphs
            })
        else:
            print(f"  Warning: No content found for {url}")

        time.sleep(1)

    except Exception as e:
        print(f"Error on {title}: {e}")

print(f"\nTotal speeches scraped: {len(results)}/{total}")

with open("president_texts_Lee_Seung_Man.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("File president_texts_Lee_Seung_Man.json created successfully!")
