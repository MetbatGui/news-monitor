import re
from typing import Optional

from domain.model import Article
from adapters.infrastructure.scrapers.base_web_scraper import BaseWebScraper


class SeoulScraper(BaseWebScraper):
    """서울경제 검색 결과를 스크래핑하는 클래스"""
    
    def build_search_url(self, keyword: str) -> str:
        return f"https://www.sedaily.com/Search/?scText={keyword}"
    
    def get_news_list_selector(self) -> str:
        return 'ul.sub_news_list.type > li'
    
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        # 제목 & 링크 추출
        title_elem = item.select_one('div.article_tit a')
        
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        link = title_elem.get('href', '')
        
        # ID 추출: https://www.sedaily.com/NewsView/2H1NFQROH4
        article_id = 0
        if link:
            match = re.search(r'/NewsView/([A-Z0-9]+)', link)
            if match:
                id_str = match.group(1)
                # 해시값이므로 숫자로 변환 (해시의 마지막 8자리를 16진수로)
                try:
                    article_id = int(id_str[-8:], 36) if len(id_str) >= 8 else hash(id_str) % 1000000000
                except:
                    article_id = hash(id_str) % 1000000000
        
        # 날짜 추출
        date_str = ''
        time_elem = item.select_one('span.rel_time')
        if time_elem:
            # "2분전", "4분전" 등의 상대 시간은 무시 (정확한 날짜가 아님)
            date_str = ''
        else:
            # 날짜와 시간이 분리되어 있는 경우
            date_elem = item.select_one('span.date')
            time_elem2 = item.select_one('span.time')
            if date_elem and time_elem2:
                date_text = date_elem.get_text(strip=True)  # "2025.12.08"
                time_text = time_elem2.get_text(strip=True)  # "14:38:07"
                # "2025.12.08 14:38:07" -> "2025-12-08 14:38:07"
                date_str = self.normalize_date(f"{date_text} {time_text}")
        
        return Article(
            id=article_id,
            title=title,
            link=link,
            date=date_str,
            keyword=keyword
        )
    
    def get_source_name(self) -> str:
        return "seoul"
