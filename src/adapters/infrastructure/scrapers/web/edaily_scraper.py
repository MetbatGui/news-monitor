import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.scrapers.base_web_scraper import BaseWebScraper


class EdailyScraper(BaseWebScraper):
    """이데일리 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://www.edaily.co.kr/search/?keyword={keyword}"
    
    def get_news_list_selector(self) -> str:
        return 'div#newsList > div.newsbox_04'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 & 링크 추출
        link_a = item.select_one('a[href^="/News/Read"]')
        if not link_a:
            return None
        
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
        
        # 날짜: 시스템 시간 사용
        date_str = self.get_current_datetime()
        
        return Article(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword
        )
    
    def get_source_name(self) -> str:
        return "이데일리"
