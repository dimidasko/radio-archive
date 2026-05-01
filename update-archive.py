# import requests
# from bs4 import BeautifulSoup
# import json
# import time
# import re
# import os

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

def scrape_entire_archive():
    # base_url = "https://www.ertecho.gr/radio/ertnewsradio/show/kathreftis/"
    # base_url = "https://www.ertecho.gr/radio/deftero/show/prepei-na-ksereis-mixani-na-kopseis-mayra-matia/"
    base_url = "https://www.ertecho.gr/radio/trito/show/anazitontas-tin-kyria-me-ti-stryxnini/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    filename = 'anazitontas-tin-kyria-me-ti-stryxnini.json'

    # Load existing data to avoid re-scraping things you already have
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    else:
        all_data = []

    existing_urls = {item['url'] for item in all_data}

    # Range 1 to 27 (inclusive)
    for page_num in range(1, 28):
        # Handle the specific URL structure
        if page_num == 1:
            current_page_url = base_url
        else:
            current_page_url = f"{base_url}page/{page_num}/"

        print(f"\n--- Scraping Page {page_num} of 27 ---")
        print(f"URL: {current_page_url}")

        try:
            res = requests.get(current_page_url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            episodes = soup.find_all('div', class_='post-content')

            if not episodes:
                print(f"No content found on page {page_num}. Ending.")
                break

            for ep in episodes:
                link_tag = ep.find('div', class_='post-title').find('a')
                session_link = link_tag['href']

                # Full URL check
                if session_link.startswith('/'):
                    session_link = "https://www.ertecho.gr" + session_link

                if session_link in existing_urls:
                    print(f"  > Skipping (Already Archived): {link_tag.get_text(strip=True)[:40]}...")
                    continue

                title = link_tag.get_text(strip=True)
                desc_div = ep.find('div', class_='article-summary')
                description = desc_div.get_text(strip=True) if desc_div else ""
                date_tag = ep.find('time', class_='entry-date')
                date_val = date_tag.get_text(strip=True) if date_tag else ""

                print(f"  + New Discovery: {title}")
                mp3_url = get_mp3_url(session_link)

                all_data.append({
                    "title": title,
                    "date": date_val,
                    "description": description,
                    "url": session_link,
                    "mp3": mp3_url
                })
                existing_urls.add(session_link)
                time.sleep(0.4) # Respectful delay

            # Save incrementally after every page is finished
            # (In case the script crashes or you stop it)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error on page {page_num}: {e}")
            continue

    print(f"\nDone! Total database size: {len(all_data)} sessions.")

if __name__ == "__main__":
    scrape_entire_archive()
