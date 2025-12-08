import re
import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime

from domain.model import Article
from ports.news_port import NewsRepository


class HankyungScraper(NewsRepository):
    """한국경제 검색 결과를 스크래핑하는 클래스"""
    
    async def fetch_reports(self, keyword: str) -> List[Article]:
        """한국경제에서 키워드로 검색한 기사 목록을 가져옵니다.
        
        Args:
            keyword: 검색할 키워드
            
        Returns:
            Article 리스트
        """
        url = f"https://search.hankyung.com/search/news?query={keyword}"
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
            
            # 뉴스 목록 컨테이너: <ul class="article">
            news_list = soup.select('ul.article > li')
            
            for item in news_list:
                try:
                    # 제목 & 링크 추출
                    # <a href="https://www.hankyung.com/article/..." target="_blank">
                    #   <em class="tit">제목</em>
                    # </a>
                    title_elem = item.select_one('em.tit')
                    link_elem = item.select_one('a[href^="https://www.hankyung.com/article/"]')
                    
                    if not title_elem or not link_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    
                    # ID 추출: https://www.hankyung.com/article/202512080227L
                    # article ID는 URL 끝부분의 숫자+문자 조합
                    article_id = 0
                    if link:
                        match = re.search(r'/article/(\d+[A-Za-z]*)$', link)
                        if match:
                            # 숫자 부분만 추출하여 ID로 사용
                            id_str = match.group(1)
                            # 숫자만 추출
                            num_match = re.search(r'(\d+)', id_str)
                            if num_match:
                                article_id = int(num_match.group(1))
                    
                    # 날짜 추출 및 포맷 변환
                    # <span class="date_time">2025.12.08 14:05</span>
                    date_elem = item.select_one('span.date_time')
                    date_str = ''
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)  # "2025.12.08 14:05"
                        # 시간이 포함된 경우와 없는 경우 처리
                        if ' ' in date_text:
                            # "2025.12.08 14:05" -> "2025-12-08 14:05"
                            date_str = date_text.replace('.', '-', 2)
                        else:
                            # "2025.12.08" -> "2025-12-08 HH:MM" (검색 시점 시간 사용)
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
            print(f"Scraping error for hankyung: {e}")
            
        return articles
