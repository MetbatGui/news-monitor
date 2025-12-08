import re
import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime

from domain.model import Article
from ports.news_port import NewsRepository


class MKScraper(NewsRepository):
    """매일경제 검색 결과를 스크래핑하는 클래스"""
    
    async def fetch_reports(self, keyword: str) -> List[Article]:
        """매일경제에서 키워드로 검색한 기사 목록을 가져옵니다.
        
        Args:
            keyword: 검색할 키워드
            
        Returns:
            Article 리스트
        """
        url = f"https://www.mk.co.kr/search?word={keyword}"
        articles = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=20)
                response.raise_for_status()
            
            # 검색 시점의 시간 기록 (HH:MM 포맷)
            current_time = datetime.now().strftime("%H:%M")
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 목록 컨테이너: <ul class="news_list ... id="list_area">
            news_list = soup.select('ul#list_area > li.news_node')
            
            for item in news_list:
                try:
                    # 제목 추출
                    # <h3 class="news_ttl">제목</h3>
                    title_elem = item.select_one('h3.news_ttl')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # 링크 & ID 추출
                    # <a href="..." class="news_item" data-id="11486777">
                    link_elem = item.select_one('a.news_item')
                    if not link_elem:
                        continue
                    
                    link = link_elem.get('href', '')
                    
                    # ID는 data-id 속성에서 추출
                    article_id = 0
                    data_id = link_elem.get('data-id', '')
                    if data_id:
                        try:
                            article_id = int(data_id)
                        except ValueError:
                            pass
                    
                    # 날짜 추출
                    # <div class="time_area"><span>12.08<br>2025</span></div>
                    # 시간 정보는 "12분 전" 같은 상대 시간이므로 현재 시각 사용
                    date_area = item.select_one('div.time_area span')
                    date_str = f"{current_date} {current_time}"
                    
                    if date_area:
                        date_text = date_area.get_text(separator=' ', strip=True)  # "12.08 2025"
                        # "12.08 2025" -> "2025-12-08"
                        parts = date_text.split()
                        if len(parts) >= 2:
                            month_day = parts[0].replace('.', '-')  # "12-08"
                            year = parts[1]  # "2025"
                            date_str = f"{year}-{month_day} {current_time}"
                    
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
            print(f"Scraping error for mk: {e}")
            
        return articles
