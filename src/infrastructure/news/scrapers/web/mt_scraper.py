import re
import httpx
from typing import Optional

from infrastructure.news.dto import ArticleData
from infrastructure.news.scrapers.base_web_scraper import BaseWebScraper
from infrastructure.network.retry_utils import common_retry


class MTScraper(BaseWebScraper):
    """머니투데이 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://www.mt.co.kr/search?keyword={keyword}&filter=title"
    
    def get_news_list_selector(self) -> str:
        return 'ul.list_wrap > li.article_item'
    
    @common_retry
    def _fetch_html(self, url: str) -> str:
        return super()._fetch_html(url)

    def parse_article(self, item, keyword: str) -> Optional[ArticleData]:
        # 링크 추출 (li > a)
        link_elem = item.select_one('a')
        if not link_elem:
            return None
        link = link_elem.get('href', '')
        
        # 제목 추출 (a > h3.headline)
        title_elem = link_elem.select_one('h3.headline')
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        
        # ID 추출: URL에서 마지막 숫자 부분
        article_id = 0
        if link:
            match = re.search(r'/(\d+)$', link)
            if match:
                article_id = int(match.group(1))
        
        # 날짜 추출
        date_elem = item.select_one('div.article_date')
        date_str = ''
        if date_elem:
            date_text = date_elem.get_text(strip=True)  # "2025.02.06 11:40"
            date_str = self.normalize_date(date_text)
        
        return ArticleData(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword,
            source=self.get_source_name()
        )
    
    def get_source_name(self) -> str:
        return "머니투데이"
