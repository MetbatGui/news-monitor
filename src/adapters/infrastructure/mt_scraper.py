import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.base_web_scraper import BaseWebScraper


class MTScraper(BaseWebScraper):
    """머니투데이 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://www.mt.co.kr/search?keyword={keyword}"
    
    def get_news_list_selector(self) -> str:
        return 'ul.list_wrap > li.article_item'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 & 링크 추출
        title_link = item.select_one('h3.headline a')
        if not title_link:
            return None
        
        title = title_link.get_text(strip=True)
        link = title_link.get('href', '')
        
        # ID 추출: URL에서 마지막 숫자 부분
        article_id = 0
        if link:
            match = re.search(r'/(\d+)$', link)
            if match:
                article_id = int(match.group(1))
        
        # 날짜 추출
        meta_span = item.select_one('div.meta span')
        date_str = ''
        if meta_span:
            date_text = meta_span.get_text(strip=True)  # "2025.12.08 14:30"
            # "2025.12.08 14:30" -> "2025-12-08 14:30"
            date_str = self.normalize_date(date_text)
        
        return Article(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword
        )
    
    def get_source_name(self) -> str:
        return "mt"
