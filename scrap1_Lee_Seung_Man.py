import requests
from bs4 import BeautifulSoup
import re
import json
import os

# Helper function to save articles to JSON
def save_to_json(articles, output_file):
    """Save articles list to JSON file"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved {len(articles)} articles to {output_file}")

# Target URL for Lee Seung Man (이승만) speeches
base_url = "https://www.pa.go.kr/online_contents/archive/president_speechIndex.jsp"
params = {
    "activePresident": "이승만"
}

output_file = "president_links_Lee_Seung_Man.json"

print("Scraping links for President Lee Seung Man (이승만)...")

# Load existing data if file exists
articles = []
if os.path.exists(output_file):
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            articles = json.load(f)
        print(f"📂 Loaded {len(articles)} existing articles from {output_file}")
    except Exception as e:
        print(f"⚠️  Could not load existing file: {e}")
        articles = []

max_pages = 200  # Increased to ensure we capture all available speeches

for page in range(1, max_pages + 1):
    print(f"Scraping page {page}...")
    try:
        # The form submits to the same URL with activePresident param
        # and sends pageIndex in the body.
        
        data = {
            "pageIndex": page,
            "activePresident": "이승만"
        }
        
        # We keep activePresident in URL as well because the form action was empty (relative to current URL)
        response = requests.post(f"{base_url}?activePresident=이승만", data=data, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Select rows in the table
        rows = soup.select("table.board-list tbody tr")
        
        # If no rows found, we've reached the end
        if not rows:
            print(f"No more articles found on page {page}. Stopping.")
            break
        
        found_on_page = 0
        for row in rows:
            subject_td = row.select_one("td.subject")
            if subject_td:
                a_tag = subject_td.find("a")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    href = a_tag.get('href')
                    
                    if href:
                        full_url = f"https://www.pa.go.kr/online_contents/archive/president_speechIndex.jsp{href}&activePresident=이승만"
                        
                        # Avoid duplicates
                        if not any(d['url'] == full_url for d in articles):
                            articles.append({
                                "title": title,
                                "url": full_url
                            })
                            found_on_page += 1
        
        print(f"  Found {found_on_page} articles on page {page}. Total so far: {len(articles)}")
        
        # Save every 20 articles
        if len(articles) > 0 and len(articles) % 20 == 0:
            save_to_json(articles, output_file)
        
        # If no new articles found on this page, we've likely reached the end
        if found_on_page == 0:
            print("No new articles found on this page. Stopping.")
            break
        
    except Exception as e:
        print(f"Error scraping page {page}: {e}")
        # Continue to next page even if there's an error
        continue

print(f"\nTotal articles found: {len(articles)}")

# Final save to JSON file
save_to_json(articles, output_file)

print(f"✅ File {output_file} created successfully!")
print(f"Scraped {len(articles)} speeches from President Lee Seung Man (이승만)")
