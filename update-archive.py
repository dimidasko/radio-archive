import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

def get_mp3_url(session_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        # Some links might be relative, ensure they are absolute
        if session_url.startswith('/'):
            session_url = "https://www.ertecho.gr" + session_url

        res = requests.get(session_url, headers=headers)
        # Use regex to find the mp3 link in the source code
        mp3_match = re.search(r'https?://[^\s"\']+\.mp3', res.text)
        return mp3_match.group(0) if mp3_match else "MP3 link not found"
    except:
        return None

def scrape_show(base_url, filename):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    # 1. Load existing data
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    else:
        all_data = []

    # Use a set for O(1) lookup speed
    existing_urls = {item['url'] for item in all_data}
    new_discoveries = []
    
    # We use a flag to break out of the nested loops
    already_caught_up = False

    # We still loop through pages just in case you haven't run the script 
    # in a long time (e.g., 20 new shows might span 2 pages)
    for page_num in range(1, 10):
        if already_caught_up:
            break
            
        current_page_url = base_url if page_num == 1 else f"{base_url}page/{page_num}/"
        print(f"Checking Page {page_num}...")
        
        try:
            res = requests.get(current_page_url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            episodes = soup.find_all('div', class_='post-content')

            if not episodes:
                break

            for ep in episodes:
                link_tag = ep.find('div', class_='post-title').find('a')
                session_link = link_tag['href']

                if session_link.startswith('/'):
                    session_link = "https://www.ertecho.gr" + session_link

                # THE CORE LOGIC: 
                # If this URL is already in our file, we have reached the end of the "new" stuff.
                if session_link in existing_urls:
                    print(f"Reached known content: {link_tag.get_text(strip=True)[:40]}")
                    already_caught_up = True
                    break 

                # If it's not in the file, it's a new session
                title = link_tag.get_text(strip=True)
                desc_div = ep.find('div', class_='article-summary')
                description = desc_div.get_text(strip=True) if desc_div else ""
                date_tag = ep.find('time', class_='entry-date')
                date_val = date_tag.get_text(strip=True) if date_tag else ""

                print(f"  + Adding new session: {title}")
                mp3_url = get_mp3_url(session_link)

                new_discoveries.append({
                    "title": title,
                    "date": date_val,
                    "description": description,
                    "url": session_link,
                    "mp3": mp3_url
                })
                time.sleep(0.4)

        except Exception as e:
            print(f"Error: {e}")
            break

    # Final Merge: Newest (first found) + Old Data
    if new_discoveries:
        updated_data = new_discoveries + all_data
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)
        print(f"Updated {filename} with {len(new_discoveries)} new items.")
    else:
        print(f"No updates needed for {filename}.")

if __name__ == "__main__":
    shows = [
        ("https://www.ertecho.gr/radio/ertnewsradio/show/kathreftis/", "kathreftis.json"),
        ("https://www.ertecho.gr/radio/deftero/show/prepei-na-ksereis-mixani-na-kopseis-mayra-matia/", "prepei-na-ksereis-mixani-na-kopseis-mayra-matia.json"),
        ("https://www.ertecho.gr/radio/trito/show/anazitontas-tin-kyria-me-ti-stryxnini/", "anazitontas-tin-kyria-me-ti-stryxnini.json"),
        ("https://www.ertecho.gr/radio/deftero/show/planodies-mousikes-deftero/","planodies-mousikes-deftero.json")
    ]
    
    for url, file in shows:
        print(f"Starting update for: {file}")
        scrape_show(url, file)
