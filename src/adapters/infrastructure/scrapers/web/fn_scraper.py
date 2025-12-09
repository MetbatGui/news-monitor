import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.scrapers.base_web_scraper import BaseWebScraper


class FnScraper(BaseWebScraper):
    """파이낸셜뉴스 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://www.fnnews.com/search?search_txt={keyword}&page=0&search_type=chronological&cont_type=tit"
    
    def get_news_list_selector(self) -> str:
        return 'ul.list_article > li'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 & 링크 추출
        title_elem = item.select_one('strong.tit_thumb a')
        
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        link = title_elem.get('href', '')
        
        # 상대 경로를 절대 경로로 변환
        if link and link.startswith('/'):
            link = 'https://www.fnnews.com' + link
        
        # ID 추출: /news/202512081501180804
        article_id = 0
        if link:
            match = re.search(r'/news/(\d+)', link)
            if match:
                article_id = int(match.group(1))
        
        # 날짜 추출
        date_elem = item.select_one('span.caption')
        date_str = ''
        if date_elem:
            date_text = date_elem.get_text(strip=True)  # "2025-12-08 15:01:05"
            # 이미 표준 형식이므로 그대로 사용
            date_str = date_text
        
        return Article(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword,
            source=self.get_source_name()
        )
    
    def get_source_name(self) -> str:
        return "파이낸셜뉴스"
