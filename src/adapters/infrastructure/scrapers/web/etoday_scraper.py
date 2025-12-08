import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.scrapers.base_web_scraper import BaseWebScraper


class EtodayScraper(BaseWebScraper):
    """이투데이 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://www.etoday.co.kr/search/?keyword={keyword}"
    
    def get_news_list_selector(self) -> str:
        return 'ul#list_W > li.sp_newslist'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 & 링크 추출
        title_elem = item.select_one('div.cluster_text_headline21 a')
        
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        link = title_elem.get('href', '')
        
        # ID 추출: https://www.etoday.co.kr/news/view/2533844
        article_id = 0
        if link:
            match = re.search(r'/news/view/(\d+)', link)
            if match:
                article_id = int(match.group(1))
        
        # 날짜 추출
        time_elem = item.select_one('div.cluster_text_press21')
        date_str = ''
        if time_elem:
            date_text = time_elem.get_text(strip=True)  # "2025-12-08 14:56"
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
        return "etoday"
