from abc import ABC, abstractmethod
from typing import List
from infrastructure.news.dto import ArticleData

class NewsRepository(ABC):
    @abstractmethod
    def fetch_reports(self, keyword: str) -> List[ArticleData]:
        """키워드로 기사 데이터를 검색하여 반환한다."""
        pass

class NewsScraper(NewsRepository):
    """뉴스 스크래퍼 인터페이스 (Repository와 동일한 역할)"""
    pass
