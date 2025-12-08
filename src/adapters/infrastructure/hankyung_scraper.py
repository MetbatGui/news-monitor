import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.base_web_scraper import BaseWebScraper


class HankyungScraper(BaseWebScraper):
    """한국경제 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://search.hankyung.com/search/news?query={keyword}"
    
    def get_news_list_selector(self) -> str:
        return 'ul.article > li'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 & 링크 추출
        title_elem = item.select_one('em.tit')
        link_elem = item.select_one('a[href^="https://www.hankyung.com/article/"]')
        
        if not title_elem or not link_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        link = link_elem.get('href', '')
        
        # ID 추출: https://www.hankyung.com/article/202512080227L
        article_id = 0
        if link:
            match = re.search(r'/article/(\d+[A-Za-z]*)$', link)
            if match:
                id_str = match.group(1)
                # 숫자만 추출
                num_match = re.search(r'(\d+)', id_str)
                if num_match:
                    article_id = int(num_match.group(1))
        
        # 날짜 추출
        date_elem = item.select_one('span.date_time')
        date_str = ''
        if date_elem:
            date_text = date_elem.get_text(strip=True)  # "2025.12.08 14:05"
            # 시간이 포함된 경우와 없는 경우 처리
            if ' ' in date_text:
                # "2025.12.08 14:05" -> "2025-12-08 14:05"
                date_str = self.normalize_date(date_text)
            else:
                # "2025.12.08" -> "2025-12-08 HH:MM" (검색 시점 시간 사용)
                date_str = self.normalize_date(date_text) + f' {self.get_current_time()}'
        
        return Article(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword
        )
    
    def get_source_name(self) -> str:
        return "hankyung"
