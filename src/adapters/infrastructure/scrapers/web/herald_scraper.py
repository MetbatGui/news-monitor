import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.scrapers.base_web_scraper import BaseWebScraper


class HeraldScraper(BaseWebScraper):
    """헤럴드경제 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://biz.heraldcorp.com/search?q={keyword}"
    
    def get_news_list_selector(self) -> str:
        return 'ul.news_list > li'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 & 링크 추출
        title_elem = item.select_one('p.news_title')
        link_elem = item.select_one('a[href*="/article/"]')
        
        if not title_elem or not link_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        link = link_elem.get('href', '')
        
        # 상대 경로를 절대 경로로 변환
        if link and link.startswith('/'):
            link = 'https://biz.heraldcorp.com' + link
        
        # ID 추출: /article/10631956
        article_id = 0
        if link:
            match = re.search(r'/article/(\d+)', link)
            if match:
                article_id = int(match.group(1))
        
        # 날짜 추출
        date_elem = item.select_one('span.date')
        date_str = ''
        if date_elem:
            date_text = date_elem.get_text(strip=True)  # "2025.12.08 15:09"
            # "2025.12.08 15:09" -> "2025-12-08 15:09"
            date_str = self.normalize_date(date_text)
        
        return Article(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword,
            source=self.get_source_name()
        )
    
    def get_source_name(self) -> str:
        return "헤럴드경제"
