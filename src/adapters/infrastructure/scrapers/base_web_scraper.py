from abc import ABC, abstractmethod
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime

from domain.model import Article
from ports.news_port import NewsRepository


class BaseWebScraper(NewsRepository, ABC):
    """웹 스크래핑 기반 뉴스 스크래퍼의 베이스 클래스
    
    공통 로직:
    - HTTP 요청 및 응답 처리
    - HTML 파싱 (BeautifulSoup)
    - 에러 처리
    - 날짜 포맷 변환 유틸리티
    
    각 스크래퍼에서 구현해야 할 부분:
    - build_search_url(): 검색 URL 생성
    - get_news_list_selector(): 뉴스 목록 CSS 셀렉터
    - parse_article(): 개별 기사 파싱
    - get_source_name(): 뉴스 소스 이름
    """
    
    # 공통 설정
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    TIMEOUT = 20
    
    async def fetch_reports(self, keyword: str) -> List[Article]:
        """뉴스 기사 목록 가져오기 (템플릿 메서드 패턴)
        
        Args:
            keyword: 검색할 키워드
            
        Returns:
            Article 리스트
        """
        url = self.build_search_url(keyword)
        articles = []
        
        try:
            html = await self._fetch_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            articles = await self._parse_articles(soup, keyword)
        except Exception as e:
            print(f"Scraping error for {self.get_source_name()}: {e}")
            
        return articles
    
    async def _fetch_html(self, url: str) -> str:
        """HTTP 요청하여 HTML 가져오기 (공통 로직)
        
        Args:
            url: 요청할 URL
            
        Returns:
            HTML 텍스트
        """
        headers = {'User-Agent': self.USER_AGENT}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.text
    
    async def _parse_articles(self, soup: BeautifulSoup, keyword: str) -> List[Article]:
        """HTML에서 기사 목록 파싱 (공통 로직 + 추상 메서드 호출)
        
        Args:
            soup: BeautifulSoup 객체
            keyword: 검색 키워드
            
        Returns:
            Article 리스트
        """
        articles = []
        selector = self.get_news_list_selector()
        news_list = soup.select(selector)
        source_name = self.get_source_name()
        
        for item in news_list:
            try:
                article = self.parse_article(item, keyword)
                if article:
                    # source 필드가 비어있으면 자동으로 채우기
                    if not article.source:
                        from dataclasses import replace
                        article = replace(article, source=source_name)
                    articles.append(article)
            except Exception as e:
                print(f"Error parsing item in {source_name}: {e}")
                continue
                
        return articles
    
    # 유틸리티 메서드
    def get_current_time(self) -> str:
        """현재 시각 반환 (HH:MM 포맷)
        
        Returns:
            현재 시각 문자열 (예: "14:30")
        """
        return datetime.now().strftime("%H:%M")
    
    def get_current_date(self) -> str:
        """현재 날짜 반환 (YYYY-MM-DD 포맷)
        
        Returns:
            현재 날짜 문자열 (예: "2025-12-08")
        """
        return datetime.now().strftime("%Y-%m-%d")
    
    def normalize_date(self, date_str: str) -> str:
        """날짜 문자열을 표준 형식으로 변환
        
        지원 형식:
        - "2025.12.08" -> "2025-12-08"
        - "2025.12.08 14:30" -> "2025-12-08 14:30"
        
        Args:
            date_str: 변환할 날짜 문자열
            
        Returns:
            표준 형식 날짜 문자열
        """
        return date_str.replace('.', '-', 2)
    
    # 추상 메서드 - 각 스크래퍼에서 구현 필요
    @abstractmethod
    def build_search_url(self, keyword: str) -> str:
        """검색 URL 생성
        
        Args:
            keyword: 검색할 키워드
            
        Returns:
            검색 URL
            
        Example:
            return f"https://www.edaily.co.kr/search/?keyword={keyword}"
        """
        pass
    
    @abstractmethod
    def get_news_list_selector(self) -> str:
        """뉴스 목록 CSS 셀렉터 반환
        
        Returns:
            CSS 셀렉터 문자열
            
        Example:
            return "div#newsList > div.newsbox_04"
        """
        pass
    
    @abstractmethod
    def parse_article(self, item, keyword: str) -> Optional[Article]:
        """개별 기사 파싱
        
        Args:
            item: BeautifulSoup element (뉴스 아이템)
            keyword: 검색 키워드
            
        Returns:
            Article 객체 또는 None (파싱 실패 시)
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """뉴스 소스 이름 반환 (로깅용)
        
        Returns:
            뉴스 소스 이름
            
        Example:
            return "edaily"
        """
        pass
