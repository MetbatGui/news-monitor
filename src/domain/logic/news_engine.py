"""기사 처리 엔진 (순수 함수)

이 모듈은 기사 필터링, 중복 체크 등의 핵심 가공 로직을 담당합니다.
모든 함수는 순수 함수로 구현되어 외부 상태에 의존하지 않으며,
같은 입력에 대해 항상 같은 출력을 보장합니다.
"""

from typing import List, Set
from infrastructure.news.dto import ArticleData


def filter_by_date(
    articles: List[ArticleData],
    target_date: str
) -> List[ArticleData]:
    """특정 날짜의 기사만 필터링 (순수 함수)
    
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
        >>> filtered = filter_by_date(articles, "2025-12-19")
        >>> len(filtered)
        1
    """
    return [
        article for article in articles
        if article.date.startswith(target_date)
    ]


def filter_new_articles(
    articles: List[ArticleData],
    seen_ids: Set[int]
) -> List[ArticleData]:
    """아직 보지 못한 새 기사만 필터링 (순수 함수)
    
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
        >>> new = filter_new_articles(articles, seen)
        >>> len(new)
        1
        >>> new[0].id
        2
    """
    return [
        article for article in articles
        if article.id not in seen_ids
    ]


def process_articles(
    articles: List[ArticleData],
    target_date: str,
    seen_ids: Set[int]
) -> List[ArticleData]:
    """기사 처리 파이프라인: 날짜 필터링 + 중복 제거 (순수 함수)
    
    이 함수는 여러 필터를 순차적으로 적용하는 함수 합성입니다.
    
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
        >>> result = process_articles(articles, "2025-12-19", seen)
        >>> len(result)
        1
        >>> result[0].id
        2
    """
    # 함수 합성: filter_by_date -> filter_new_articles
    filtered_by_date = filter_by_date(articles, target_date)
    return filter_new_articles(filtered_by_date, seen_ids)


def sort_articles_by_date(articles: List[ArticleData]) -> List[ArticleData]:
    """기사를 날짜 역순(최신순)으로 정렬 (순수 함수)
    
    Args:
        articles: 정렬할 기사 목록
        
    Returns:
        날짜 역순으로 정렬된 기사 목록
        
    Examples:
        >>> articles = [
        ...     ArticleData(id=1, date="2025-12-19 10:00", ...),
        ...     ArticleData(id=2, date="2025-12-19 15:00", ...)
        ... ]
        >>> sorted_articles = sort_articles_by_date(articles)
        >>> sorted_articles[0].id
        2
    """
    return sorted(articles, key=lambda x: x.date, reverse=True)
