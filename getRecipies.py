import requests
from bs4 import BeautifulSoup
import os
import random

def get_existing_urls(filename):
    """Reads the current file and returns a set of URLs already saved."""
    if not os.path.exists(filename):
        return set()
    with open(filename, "r") as f:
        return set(line.strip() for line in f if line.strip())

def scrape_random_allrecipes(existing_urls, target_new_count=500):
    """Gathers a large pool of URLs from multiple sitemaps using lxml."""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    url_pool = []
    sitemap_range = range(1, 21) 

    print(f"Gathering recipe pool from {len(sitemap_range)} sitemaps using lxml...")
    
    for i in sitemap_range:
        sitemap_url = f"https://www.allrecipes.com/sitemap_{i}.xml"
        print(f"  -> Reading sitemap {i}...", end="\r")
        
        try:
            response = requests.get(sitemap_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Use 'xml' features with the lxml backend
            soup = BeautifulSoup(response.content, features="xml")
            locs = soup.find_all('loc')
            
            for loc in locs:
                url = loc.text.strip()
                if "/recipe/" in url and url not in existing_urls:
                    url_pool.append(url)
                    
        except Exception as e:
            print(f"\n  [!] Skipping sitemap {i}: {e}")
            continue

    print(f"\nFound {len(url_pool)} new recipes available. Shuffling...")
    
    if not url_pool:
        return []

    random.shuffle(url_pool)
    return url_pool[:target_new_count]

def main():
    filename = "mealie_import_list.txt"
    target_new = 500 
    
    existing = get_existing_urls(filename)
    print(f"Current list contains {len(existing)} recipes.")
    
    new_found = scrape_random_allrecipes(existing, target_new)
    
    if new_found:
        with open(filename, "a") as f:
            for url in new_found:
                f.write(url + "\n")
        print(f"Success! Added {len(new_found)} RANDOM new recipes to {filename}.")
        print(f"Total list size: {len(existing) + len(new_found)}")
    else:
        print("No new recipes found.")

if __name__ == "__main__":
    main()