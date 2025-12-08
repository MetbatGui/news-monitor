import re
import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime

from domain.model import Article
from ports.news_port import NewsRepository


class EdailyScraper(NewsRepository):
    """이데일리 검색 결과를 스크래핑하는 클래스"""
    
    async def fetch_reports(self, keyword: str) -> List[Article]:
        """이데일리에서 키워드로 검색한 기사 목록을 가져옵니다.
        
        Args:
            keyword: 검색할 키워드
            
        Returns:
            Article 리스트
        """
        url = f"https://www.edaily.co.kr/search/?keyword={keyword}"
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
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 목록 컨테이너: <div id="newsList">
            news_list = soup.select('div#newsList > div.newsbox_04')
            
            for item in news_list:
                try:
                    # 제목 & 링크 추출
                    # <a href="/News/Read?newsId=...&mediaCodeNo=..." title="제목">
                    link_a = item.select_one('a[href^="/News/Read"]')
                    if not link_a:
                        continue
                    
                    title = link_a.get('title', '').strip()
                    link = link_a.get('href', '')
                    
                    # 상대 경로를 절대 경로로 변환
                    if link and not link.startswith('http'):
                        link = 'https://www.edaily.co.kr' + link
                    
                    # ID 추출: newsId=03276726642396552
                    article_id = 0
                    if link:
                        match = re.search(r'newsId=(\d+)', link)
                        if match:
                            article_id = int(match.group(1))
                    
                    # 날짜 추출 및 포맷 변환
                    # <div class="author_category">2025.12.08 ...</div>
                    date_elem = item.select_one('div.author_category')
                    date_text = ''
                    if date_elem:
                        # 첫 번째 텍스트 노드에서 날짜 추출 (2025.12.08)
                        text_parts = date_elem.get_text(strip=True).split()
                        if text_parts:
                            date_text = text_parts[0]  # "2025.12.08"
                    
                    # "2025.12.08" -> "2025-12-08 HH:MM" (검색 시점의 시간 사용)
                    date_str = ''
                    if date_text:
                        date_str = date_text.replace('.', '-') + f' {current_time}'
                    
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
            print(f"Scraping error for edaily: {e}")
            
        return articles
