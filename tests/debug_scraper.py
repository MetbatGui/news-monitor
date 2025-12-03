import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from src.config import Config

def debug_scraper():
    url = Config.TARGET_URL
    print(f"Fetching {url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    with open("newspim_debug.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved to newspim_debug.html")

if __name__ == "__main__":
    debug_scraper()
