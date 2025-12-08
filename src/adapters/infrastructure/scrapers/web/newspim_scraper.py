import re
import httpx
from bs4 import BeautifulSoup
from typing import List

from domain.model import Article
from ports.news_port import NewsRepository
from config import Config

class NewspimScraper(NewsRepository):
    async def fetch_reports(self, keyword: str) -> List[Article]:
        # URL dynamic generation
        url = f"https://www.newspim.com/search?searchword={keyword}"
        articles = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=20)
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # User provided structure:
            # <article class="thumb_h"> ... </article>
            items = soup.select('article.thumb_h')
            
            for item in items:
                try:
                    # Title & Link
                    # <div class="txt"> <strong class="subject"> <a href="..."> ... </a> </strong>
                    subject_a = item.select_one('div.txt > strong.subject > a')
                    if not subject_a:
                        continue
                        
                    title = subject_a.get_text(strip=True)
                    link = subject_a.get('href')
                    
                    if link and not link.startswith('http'):
                        link = 'https://www.newspim.com' + link
                        
                    # ID Extraction from link
                    # href="/news/view/20251203000832"
                    article_id = 0
                    if link:
                        match = re.search(r'/view/(\d+)', link)
                        if match:
                            article_id = int(match.group(1))
                    
                    # Date
                    # <span class="date">2025-12-03 13:40</span>
                    date_elem = item.select_one('span.date')
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    
                    articles.append(Article(
                        id=article_id,
                        title=title,
                        link=link,
                        date=date_str,
                        keyword=keyword,
                        source="뉴스핌"
                    ))
                    
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Scraping error: {e}")
            
        return articles

    def get_source_name(self) -> str:
        return "뉴스핌"
