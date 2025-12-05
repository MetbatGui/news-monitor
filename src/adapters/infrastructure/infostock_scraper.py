import re
import requests
from bs4 import BeautifulSoup
from typing import List

from domain.model import Article
from ports.news_port import NewsRepository

class InfostockScraper(NewsRepository):
    BASE_URL = "https://www.infostockdaily.co.kr"
    SEARCH_URL = "https://www.infostockdaily.co.kr/news/articleList.html"

    def fetch_reports(self, keyword: str) -> List[Article]:
        articles = []
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                "Referer": "https://www.infostockdaily.co.kr/news/articleList.html"
            }
            
            data = {
                "sc_area": "A",
                "view_type": "sm",
                "sc_word": keyword
            }
            
            response = requests.post(self.SEARCH_URL, headers=headers, data=data, timeout=20)
            response.raise_for_status()
            # Fix encoding issue
            # Fix encoding issue
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select(".list-block")
            
            for item in items:
                try:
                    # Title & Link
                    title_tag = item.select_one(".list-titles a")
                    if not title_tag:
                        continue
                        
                    title = title_tag.text.strip()
                    relative_link = title_tag['href']
                    link = self.BASE_URL + relative_link
                    
                    # ID Extraction
                    # Link format: /news/articleView.html?idxno=12345
                    article_id = 0
                    match = re.search(r'idxno=(\d+)', relative_link)
                    if match:
                        article_id = int(match.group(1))
                    else:
                        # Fallback if ID not found in URL (unlikely for this CMS)
                        continue

                    # Date
                    # Format: "2025-12-04 16:16" or similar
                    date_tag = item.select_one(".list-dated")
                    date_str = date_tag.text.strip() if date_tag else ""
                    
                    # Clean up date string if it contains extra info (e.g. " | 기자명")
                    # Usually it's just date/time or "Author | Date"
                    # Let's try to extract just the date/time part if possible, or keep as is.
                    # The user's code just prints it. We'll keep it as is for now, 
                    # but typically we want "YYYY-MM-DD HH:MM" for consistency.
                    # Example: "2024.12.04 16:20" or "기자명 | 2024.12.04 16:20"
                    # Simple regex to find date pattern might be good, but let's stick to raw first.
                    
                    articles.append(Article(
                        id=article_id,
                        title=title,
                        link=link,
                        date=date_str,
                        keyword=keyword
                    ))
                    
                except Exception as e:
                    print(f"Error parsing Infostock item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Infostock scraping error: {e}")
            
        return articles
