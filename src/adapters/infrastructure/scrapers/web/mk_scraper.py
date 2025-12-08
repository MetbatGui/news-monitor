import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.scrapers.base_web_scraper import BaseWebScraper


class MKScraper(BaseWebScraper):
    """매일경제 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://www.mk.co.kr/search?word={keyword}"
    
    def get_news_list_selector(self) -> str:
        return 'ul#list_area > li.news_node'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 추출
        title_elem = item.select_one('h3.news_ttl')
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        
        # 링크 & ID 추출
        link_elem = item.select_one('a.news_item')
        if not link_elem:
            return None
        
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
        date_area = item.select_one('div.time_area span')
        date_str = f"{self.get_current_date()} {self.get_current_time()}"
        
        if date_area:
            date_text = date_area.get_text(separator=' ', strip=True)  # "12.08 2025"
            # "12.08 2025" -> "2025-12-08"
            parts = date_text.split()
            if len(parts) >= 2:
                month_day = parts[0].replace('.', '-')  # "12-08"
                year = parts[1]  # "2025"
                date_str = f"{year}-{month_day} {self.get_current_time()}"
        
        return Article(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword
        )
    
    def get_source_name(self) -> str:
        return "mk"
