import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.scrapers.base_web_scraper import BaseWebScraper


class YonhapScraper(BaseWebScraper):
    """연합뉴스 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://www.yna.co.kr/search/index?query={keyword}"
    
    def get_news_list_selector(self) -> str:
        return 'ul.list01 > li'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 & 링크 추출
        title_elem = item.select_one('span.title01')
        link_elem = item.select_one('a[href^="https://www.yna.co.kr/view/"]')
        
        if not title_elem or not link_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        link = link_elem.get('href', '')
        
        # ID 추출: https://www.yna.co.kr/view/AKR20251208089300053?section=search
        article_id = 0
        if link:
            match = re.search(r'/view/([A-Z0-9]+)', link)
            if match:
                id_str = match.group(1)
                # 숫자만 추출
                num_match = re.search(r'(\d+)', id_str)
                if num_match:
                    article_id = int(num_match.group(1))
        
        # 날짜 추출
        time_elem = item.select_one('span.txt-time')
        date_str = ''
        if time_elem:
            date_text = time_elem.get_text(strip=True)  # "2025-12-08 14:19"
            # 이미 표준 형식이므로 그대로 사용
            date_str = date_text
        
        return Article(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword
        )
    
    def get_source_name(self) -> str:
        return "yonhap"
