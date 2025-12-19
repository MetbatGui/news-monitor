"""기사 처리 엔진 (순수 함수)"""

from typing import Set, List
from infrastructure.news.dto import ArticleData


class NewsEngine:
    """기사 처리 엔진 (순수 함수 집합)
    
    이 클래스는 "어떤 기사를 처리할 것인가?"에 대한 비즈니스 규칙을 담당합니다.
    모든 메서드는 순수 함수로 구현되어 부작용이 없습니다.
    """
    
    @staticmethod
    def filter_by_date(
        articles: List[ArticleData],
        target_date: str
    ) -> List[ArticleData]:
        """특정 날짜의 기사만 필터링
        
        Args:
            articles: 기사 데이터 목록
            target_date: 대상 날짜 (YYYY-MM-DD 형식)
            
        Returns:
            필터링된 기사 목록
            
        Examples:
            >>> articles = [
            ...     ArticleData(id=1, date="2025-12-19 10:00", ...),
            ...     ArticleData(id=2, date="2025-12-18 15:00", ...)
            ... ]
            >>> filtered = NewsEngine.filter_by_date(articles, "2025-12-19")
            >>> len(filtered)
            1
        """
        return [
            article for article in articles
            if article.date.startswith(target_date)
        ]
    
    @staticmethod
    def filter_new_articles(
        articles: List[ArticleData],
        seen_ids: Set[int]
    ) -> List[ArticleData]:
        """아직 보지 못한 새 기사만 필터링
        
        Args:
            articles: 기사 데이터 목록
            seen_ids: 이미 본 기사 ID 세트
            
        Returns:
            새로운 기사 목록
            
        Examples:
            >>> articles = [
            ...     ArticleData(id=1, ...),
            ...     ArticleData(id=2, ...)
            ... ]
            >>> seen = {1}
            >>> new_articles = NewsEngine.filter_new_articles(articles, seen)
            >>> len(new_articles)
            1
            >>> new_articles[0].id
            2
        """
        return [
            article for article in articles
            if article.id not in seen_ids
        ]
    
    @staticmethod
    def process_articles(
        articles: List[ArticleData],
        target_date: str,
        seen_ids: Set[int]
    ) -> List[ArticleData]:
        """기사 처리 파이프라인 (날짜 필터링 + 중복 제거)
        
        이 메서드는 여러 필터를 순차적으로 적용하는 파이프라인입니다.
        
        Args:
            articles: 원시 기사 데이터 목록
            target_date: 대상 날짜 (YYYY-MM-DD)
            seen_ids: 이미 본 기사 ID 세트
            
        Returns:
            처리할 새 기사 목록
            
        Examples:
            >>> articles = [
            ...     ArticleData(id=1, date="2025-12-19 10:00", ...),
            ...     ArticleData(id=2, date="2025-12-19 11:00", ...),
            ...     ArticleData(id=3, date="2025-12-18 12:00", ...)
            ... ]
            >>> seen = {1}
            >>> result = NewsEngine.process_articles(articles, "2025-12-19", seen)
            >>> len(result)
            1
            >>> result[0].id
            2
        """
        # 함수 합성: filter_by_date -> filter_new_articles
        filtered_by_date = NewsEngine.filter_by_date(articles, target_date)
        return NewsEngine.filter_new_articles(filtered_by_date, seen_ids)
