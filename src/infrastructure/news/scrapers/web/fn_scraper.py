import re
import httpx
import logging
from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import quote

from infrastructure.news.dto import ArticleData
from infrastructure.news.scrapers.base_web_scraper import BaseWebScraper
from infrastructure.network.retry_utils import common_retry

logger = logging.getLogger(__name__)


class FnScraper(BaseWebScraper):
    """파이낸셜뉴스 검색 결과를 스크래핑하는 클래스"""
    
    SEARCH_URL = "https://www.fnnews.com/search/load/list"

    def fetch_reports(self, keyword: str) -> List[ArticleData]:
        articles = []
        try:
            html = self._fetch_search_result(keyword)
            # Response is HTML fragment to be injected into #listArea
            # Likely contains <div class="list_art"> or similar
            soup = BeautifulSoup(html, 'html.parser')
            # The base class _parse_articles expects a soup and calls get_news_list_selector
            # Let's adjust parsing if needed. 
            # Note: The original generic _parse_articles finds selector and loops.
            # If the fragment is just a list of items, we might need to adjust selector.
            
            articles = self._parse_articles(soup, keyword)
            
        except Exception as e:
            logger.error(f"{self.get_source_name()} 스크래핑 오류: {e}", exc_info=True)
            
        return articles

    @common_retry
    def _fetch_search_result(self, keyword: str) -> str:
        encoded_keyword = quote(keyword)
        # Referer URL matches the page where the AJAX call originates
        referrer_url = f'https://www.fnnews.com/search?search_txt={encoded_keyword}&page=0&search_type=chronological&cont_type=tit'
        
        headers = {
            'User-Agent': self.USER_AGENT,
        }
        
        data = {
            "page": "0",
            "search_type": "chronological",
            "cont_type": "tit",
            "period_type": "",
            "searchDateS": "",
            "searchDateE": "",
            "search_txt": keyword,
        }
        
        with httpx.Client(timeout=self.TIMEOUT) as client:
            # 1. GET to establish session (cookies)
            client.get(referrer_url, headers=headers)
            
            # 2. POST for data
            headers['X-Requested-With'] = 'XMLHttpRequest'
            headers['Referer'] = referrer_url
            headers['Origin'] = 'https://www.fnnews.com'
            
            response = client.post(self.SEARCH_URL, headers=headers, data=data)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text

    def build_search_url(self, keyword: str) -> str:
        # Not used in new fetch_reports but kept for reference
        return f"https://www.fnnews.com/search?search_txt={keyword}&page=0&search_type=chronological&cont_type=tit"
    
    def get_news_list_selector(self) -> str:
        # The structure needs to be checked from the response.
        # Original was 'ul.list_article > li'
        # Let's assume it's roughly the same for now, or use a broader one.
        # In the main page HTML I saw, <div class="wrap_artList" id="listArea">.
        # Often these return <ul>...</ul>.
        return 'li' # Try generic li if parsing fragment, or keep original if it wraps in ul

    
    def parse_article(self, item, keyword: str) -> Optional[ArticleData]:
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
        
        return ArticleData(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword,
            source=self.get_source_name()
        )
    
    def get_source_name(self) -> str:
        return "파이낸셜뉴스"
