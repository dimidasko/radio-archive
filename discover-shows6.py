import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta

def get_slug(url):
    """Extracts the show slug from a URL, e.g., 'kathreftis'."""
    if not url or '/show/' not in url:
        return None
    # Strips everything but the part between /show/ and the next slash
    parts = url.split('/show/')
    if len(parts) > 1:
        return parts[1].strip('/').split('/')[0]
    return None

def scrape_full_week(base_program_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    domain = "https://www.ertecho.gr"
    schedule_data = {}

    # Greek day mapping for the "Σήμερα" replacement
    greek_days = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]

    try:
        res = requests.get(base_program_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        today_link = soup.find('a', class_='item active', string=lambda s: s and 'ΣΗΜΕΡΑ' in s)
        if not today_link: return {}

        # --- LOGIC TO CONVERT "ΣΗΜΕΡΑ" TO ACTUAL DATE ---
        tomorrow_link = today_link.find_next_sibling('a', class_='item')
        today_label = "Σήμερα" # Fallback
        
        if tomorrow_link and 'dt=' in tomorrow_link['href']:
            # Extract date from tomorrow: ?dt=2026-05-02
            tomorrow_str = tomorrow_link['href'].split('dt=')[1].split('&')[0]
            tomorrow_date = datetime.strptime(tomorrow_str, '%Y-%m-%d')
            
            # Subtract 1 day to get today
            today_date = tomorrow_date - timedelta(days=1)
            
            # Format as "DD/MM DayName"
            day_name = greek_days[today_date.weekday()]
            today_label = today_date.strftime(f'%d/%m {day_name}')

        # Collect 7 days starting with our new today_label
        target_links = [today_link]
        next_sibling = today_link.find_next_sibling('a', class_='item')
        while next_sibling and len(target_links) < 7:
            target_links.append(next_sibling)
            next_sibling = next_sibling.find_next_sibling('a', class_='item')

        for i, link in enumerate(target_links):
            # Use our calculated label for the first index, otherwise use the link text
            day_label = today_label if i == 0 else link.get_text(strip=True)
            day_url = domain + link['href'] if link['href'].startswith('/') else link['href']
            
            day_res = requests.get(day_url, headers=headers)
            day_soup = BeautifulSoup(day_res.text, 'html.parser')
            container = day_soup.find('div', class_='articles-list column')
            if not container: continue

            for ep in container.find_all('div', class_='post-content'):
                time_tag = ep.find('div', class_='broadcast-time')
                show_tag = ep.find('a', class_='show-name')
                
                if time_tag and show_tag:
                    # Remove all whitespace/newlines from time
                    t_val = "".join(time_tag.get_text().split()) 
                    s_slug = get_slug(show_tag.get('href', ''))
                    
                    if s_slug:
                        if s_slug not in schedule_data:
                            schedule_data[s_slug] = []
                        schedule_data[s_slug].append(f"{day_label} {t_val}")
            
            time.sleep(0.2)

        return {slug: " | ".join(times) for slug, times in schedule_data.items()}

    except Exception as e:
        print(f"Error in week scrape: {e}")
        return {}

def discover_all_comprehensive():
    # Only national stations slugs
    MAIN_STATION_SLUGS = ['ertnewsradio', 'proto', 'deftero', 'trito', 'kosmos', 'i-foni-tis-elladas', 'r-s-makedonias']
    
    # 1. Get Stations
    url = "https://www.ertecho.gr/ondemand/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = soup.select('ul.sub-menu a[href*="/program/"]')
    
    master_list = []

    for link in links:
        href = link['href']
        if not any(slug in href for slug in MAIN_STATION_SLUGS): continue
        
        name = link.get_text(strip=True).replace("Πρόγραμμα ", "")
        prog_url = "https://www.ertecho.gr" + href if href.startswith('/') else href
        
        print(f"\nProcessing Station: {name}")
        
        # 2. Get Weekly Schedule (mapped by SLUG)
        station_schedule = scrape_full_week(prog_url)
        
        # 3. Get On-Demand shows
        ondemand_url = prog_url.replace('/program/', '/?post_type=ondemand')
        od_res = requests.get(ondemand_url, headers=headers)
        od_soup = BeautifulSoup(od_res.text, 'html.parser')
        
        for od_link in od_soup.select('a[href*="/show/"]'):
            full_url = od_link['href']
            if not full_url.startswith('http'): full_url = "https://www.ertecho.gr" + full_url
            
            # Standardize URL
            full_url = full_url.split('/ondemand/')[0]
            if not full_url.endswith('/'): full_url += '/'
            
            title = od_link.get_text(strip=True)
            slug = get_slug(full_url)

            if not title or not slug: continue

            # MATCHING BY SLUG
            air_time = station_schedule.get(slug, "Not listed in weekly program")

            if full_url not in [s['url'] for s in master_list]:
                master_list.append({
                    "station": name,
                    "title": title,
                    "url": full_url,
                    "air_time": air_time,
                    "filename": f"{slug}.json"
                })

    with open('available_shows.json', 'w', encoding='utf-8') as f:
        json.dump(master_list, f, ensure_ascii=False, indent=4)
    print(f"\nSuccess! Found {len(master_list)} shows.")

if __name__ == "__main__":
    discover_all_comprehensive()

