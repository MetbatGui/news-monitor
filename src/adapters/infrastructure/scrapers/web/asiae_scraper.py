import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.scrapers.base_web_scraper import BaseWebScraper


class AsiaeScraper(BaseWebScraper):
    """아시아경제 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://www.asiae.co.kr/search/index.htm?keyword={keyword}"
    
    def get_news_list_selector(self) -> str:
        return 'div.section_list > div.article_type'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 & 링크 추출
        title_elem = item.select_one('h1 > a > strong')
        link_elem = item.select_one('h1 > a[href*="/article/"]')
        
        if not title_elem or not link_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        link = link_elem.get('href', '')
        
        # 상대 경로를 절대 경로로 변환
        if link and link.startswith('//'):
            link = 'https:' + link
        
        # ID 추출: //www.asiae.co.kr/article/2025120815042032476
        article_id = 0
        if link:
            match = re.search(r'/article/(\d+)', link)
            if match:
                article_id = int(match.group(1))
        
        # 날짜 추출
        time_elem = item.select_one('p.rel_time')
        date_str = ''
        if time_elem:
            date_text = time_elem.get_text(strip=True)  # "2025.12.08 15:04:20"
            # "2025.12.08 15:04:20" -> "2025-12-08 15:04:20"
            date_str = self.normalize_date(date_text)
        
        return Article(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword
        )
    
    def get_source_name(self) -> str:
        return "asiae"
