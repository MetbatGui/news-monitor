import re
import httpx
from bs4 import BeautifulSoup
from typing import List

from domain.model import Article
from ports.news_port import NewsRepository


class MTScraper(NewsRepository):
    """머니투데이 검색 결과를 스크래핑하는 클래스"""
    
    async def fetch_reports(self, keyword: str) -> List[Article]:
        """머니투데이에서 키워드로 검색한 기사 목록을 가져옵니다.
        
        Args:
            keyword: 검색할 키워드
            
        Returns:
            Article 리스트
        """
        url = f"https://www.mt.co.kr/search?keyword={keyword}"
        articles = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=20)
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 목록 컨테이너: <ul class="list_wrap">
            news_list = soup.select('ul.list_wrap > li.article_item')
            
            for item in news_list:
                try:
                    # 제목 & 링크 추출
                    # <h3 class="headline"><a href="...">제목</a></h3>
                    title_link = item.select_one('h3.headline a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    link = title_link.get('href', '')
                    
                    # ID 추출: URL에서 마지막 숫자 부분
                    # https://www.mt.co.kr/future/2025/12/08/2025120811411697807
                    article_id = 0
                    if link:
                        match = re.search(r'/(\d+)$', link)
                        if match:
                            article_id = int(match.group(1))
                    
                    # 날짜 추출
                    # <div class="meta"><span>2025.12.08 14:30</span>
                    meta_span = item.select_one('div.meta span')
                    date_str = ''
                    if meta_span:
                        date_text = meta_span.get_text(strip=True)  # "2025.12.08 14:30"
                        # "2025.12.08 14:30" -> "2025-12-08 14:30"
                        date_str = date_text.replace('.', '-', 2)
                    
                    articles.append(Article(
                        id=article_id,
                        title=title,
                        link=link,
                        date=date_str,
                        keyword=keyword
                    ))
                    
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Scraping error for mt: {e}")
            
        return articles
