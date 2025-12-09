import httpx
import re
import xml.etree.ElementTree as ET
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from domain.model import Article
from ports.news_port import NewsRepository

logger = logging.getLogger(__name__)


class MKRssScraper(NewsRepository):
    """매일경제 RSS 피드에서 뉴스를 가져오는 스크래퍼"""
    
    def __init__(self, rss_url: str = "https://www.mk.co.kr/rss/40300001/"):
        self.rss_url = rss_url
    
    async def fetch_reports(self, keyword: str = "") -> List[Article]:
        """RSS 피드에서 뉴스를 가져옵니다.
        
        Args:
            keyword: 필터링할 키워드 (제목에서만 검색)
                    빈 문자열이면 모든 항목 반환
        
        Returns:
            Article 리스트
        """
        articles = []
        
        # RSS XML 가져오기
        root = await self._fetch_rss_content()
        if root is None:
            return articles
        
        # 각 item 처리
        for item in root.findall('.//item'):
            article = self._process_rss_item(item, keyword)
            if article:
                articles.append(article)
        
        return articles
    
    async def _fetch_rss_content(self) -> Optional[ET.Element]:
        """RSS XML 콘텐츠를 가져와서 파싱합니다.
        
        Returns:
            파싱된 XML root element, 실패시 None
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(self.rss_url, headers=headers, timeout=20)
                response.raise_for_status()
            
            return ET.fromstring(response.content)
        except Exception as e:
            logger.error(f"RSS 가져오기 오류: {e}", exc_info=True)
            return None
    
    def _process_rss_item(self, item: ET.Element, keyword: str) -> Optional[Article]:
        """단일 RSS item을 처리하여 Article로 변환합니다.
        
        Args:
            item: RSS item element
            keyword: 필터링할 키워드
            
        Returns:
            Article 객체, 필터링되거나 오류시 None
        """
        try:
            # 필드 추출
            fields = self._extract_item_fields(item)
            
            # 키워드 필터링 (제목에서만)
            if keyword and not self._matches_keyword(keyword, fields['title']):
                return None
            
            # Article 생성
            return self._create_article_from_fields(fields, keyword)
            
        except Exception as e:
            logger.debug(f"RSS 항목 파싱 오류: {e}")
            return None
    
    def _extract_item_fields(self, item: ET.Element) -> dict:
        """RSS item에서 필드를 추출합니다.
        
        Args:
            item: RSS item element
            
        Returns:
            추출된 필드 dict
        """
        return {
            'no': self._get_element_text(item.find('no')),
            'title': self._get_element_text(item.find('title')),
            'link': self._get_element_text(item.find('link')),
            'category': self._get_element_text(item.find('category')),
            'pub_date': self._get_element_text(item.find('pubDate')),
            'author': self._get_element_text(item.find('author'))
        }
    
    def _get_element_text(self, element: Optional[ET.Element]) -> str:
        """XML Element에서 텍스트를 안전하게 추출합니다.
        
        Args:
            element: XML Element (None 가능)
            
        Returns:
            Element의 text 또는 빈 문자열
        """
        return element.text if element is not None and element.text else ""
    
    def _matches_keyword(self, keyword: str, title: str) -> bool:
        """키워드가 제목에 포함되는지 확인합니다.
        
        Args:
            keyword: 검색 키워드
            title: 제목
            
        Returns:
            매칭 여부
        """
        return keyword.lower() in title.lower()
    
    def _create_article_from_fields(self, fields: dict, keyword: str) -> Article:
        """추출된 필드로 Article 객체를 생성합니다.
        
        Args:
            fields: _extract_item_fields에서 반환된 필드 dict
            keyword: 검색 키워드
            
        Returns:
            Article 객체
        """
        article_id = self._extract_news_id(fields['no'])
        date_str = self._convert_date_format(fields['pub_date'])
        
        return Article(
            id=article_id,
            title=fields['title'],
            link=fields['link'],
            date=date_str,
            keyword=keyword if keyword else fields['category'],
            source=self.get_source_name()
        )
    
    def _extract_news_id(self, no: str) -> int:
        """no 필드에서 뉴스 ID 추출
        
        Args:
            no: 뉴스 번호 (예: "11487648")
            
        Returns:
            뉴스 ID (정수)
        """
        try:
            return int(no) if no else 0
        except ValueError:
            return 0
    
    def _convert_date_format(self, pub_date: str) -> str:
        """RFC-822 날짜를 YYYY-MM-DD HH:MM 포맷으로 변환
        
        Args:
            pub_date: RFC-822 형식 날짜 (예: "Tue, 09 Dec 2025 14:21:46 +09:00")
            
        Returns:
            변환된 날짜 문자열 (예: "2025-12-09 14:21")
        """
        try:
            # "+09:00" 같은 timezone을 제거하고 파싱
            date_without_tz = pub_date.rsplit(' ', 1)[0] if '+' in pub_date else pub_date
            dt = datetime.strptime(date_without_tz, "%a, %d %b %Y %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            logger.warning(f"날짜 변환 오류 '{pub_date}': {e}")
            return pub_date
    
    def get_source_name(self) -> str:
        return "매일경제"
