"""news_engine 순수 함수 테스트

이 테스트는 Mock 없이 순수 함수의 입출력만 검증합니다.
"""

import pytest
from dataclasses import dataclass

from infrastructure.news.dto import ArticleData
from domain.logic import news_engine


# 테스트 픽스처: 샘플 기사 데이터
@pytest.fixture
def sample_articles():
    """테스트용 샘플 기사 목록"""
    return [
        ArticleData(
            id=1,
            title="기사1",
            link="https://example.com/1",
            date="2025-12-19 10:00",
            keyword="테스트",
            source="뉴스1"
        ),
        ArticleData(
            id=2,
            title="기사2",
            link="https://example.com/2",
            date="2025-12-19 15:00",
            keyword="테스트",
            source="뉴스2"
        ),
        ArticleData(
            id=3,
            title="기사3",
            link="https://example.com/3",
            date="2025-12-18 12:00",
            keyword="테스트",
            source="뉴스3"
        ),
    ]


class TestFilterByDate:
    """filter_by_date 함수 테스트"""
    
    def test_filter_today_articles(self, sample_articles):
        """오늘 날짜의 기사만 필터링"""
        # When
        result = news_engine.filter_by_date(sample_articles, "2025-12-19")
        
        # Then
        assert len(result) == 2
        assert all(a.date.startswith("2025-12-19") for a in result)
    
    def test_filter_yesterday_articles(self, sample_articles):
        """어제 날짜의 기사만 필터링"""
        # When
        result = news_engine.filter_by_date(sample_articles, "2025-12-18")
        
        # Then
        assert len(result) == 1
        assert result[0].id == 3
    
    def test_filter_no_matches(self, sample_articles):
        """일치하는 기사가 없을 때 빈 리스트"""
        # When
        result = news_engine.filter_by_date(sample_articles, "2025-12-20")
        
        # Then
        assert result == []
    
    def test_empty_input(self):
        """빈 리스트 입력 시 빈 리스트 반환"""
        # When
        result = news_engine.filter_by_date([], "2025-12-19")
        
        # Then
        assert result == []


class TestFilterNewArticles:
    """filter_new_articles 함수 테스트"""
    
    def test_exclude_seen_articles(self, sample_articles):
        """이미 본 기사는 제외"""
        # Given
        seen_ids = {1, 3}
        
        # When
        result = news_engine.filter_new_articles(sample_articles, seen_ids)
        
        # Then
        assert len(result) == 1
        assert result[0].id == 2
    
    def test_all_new_articles(self, sample_articles):
        """모든 기사가 새로운 경우"""
        # Given
        seen_ids = set()
        
        # When
        result = news_engine.filter_new_articles(sample_articles, seen_ids)
        
        # Then
        assert len(result) == 3
        assert result == sample_articles
    
    def test_all_seen_articles(self, sample_articles):
        """모든 기사를 이미 본 경우"""
        # Given
        seen_ids = {1, 2, 3}
        
        # When
        result = news_engine.filter_new_articles(sample_articles, seen_ids)
        
        # Then
        assert result == []


class TestProcessArticles:
    """process_articles 함수 테스트 (파이프라인)"""
    
    def test_filter_and_exclude(self, sample_articles):
        """날짜 필터링 + 중복 제거 파이프라인"""
        # Given
        seen_ids = {1}  # ID 1은 이미 봄
        
        # When
        result = news_engine.process_articles(
            sample_articles,
            "2025-12-19",
            seen_ids
        )
        
        # Then
        assert len(result) == 1
        assert result[0].id == 2  # ID 2만 남음 (오늘 날짜 + 새 기사)
    
    def test_no_new_articles_for_today(self, sample_articles):
        """오늘 날짜의 새 기사가 없을 때"""
        # Given
        seen_ids = {1, 2}  # 오늘 기사 모두 이미 봄
        
        # When
        result = news_engine.process_articles(
            sample_articles,
            "2025-12-19",
            seen_ids
        )
        
        # Then
        assert result == []


class TestSortArticlesByDate:
    """sort_articles_by_date 함수 테스트"""
    
    def test_sort_descending(self, sample_articles):
        """최신순 정렬 (역순)"""
        # When
        result = news_engine.sort_articles_by_date(sample_articles)
        
        # Then
        assert result[0].id == 2  # 2025-12-19 15:00
        assert result[1].id == 1  # 2025-12-19 10:00
        assert result[2].id == 3  # 2025-12-18 12:00
    
    def test_single_article(self):
        """단일 기사는 그대로 반환"""
        # Given
        articles = [
            ArticleData(
                id=1,
                title="기사",
                link="https://example.com",
                date="2025-12-19 10:00",
                keyword="test",
                source="news"
            )
        ]
        
        # When
        result = news_engine.sort_articles_by_date(articles)
        
        # Then
        assert len(result) == 1
        assert result[0].id == 1
    
    def test_empty_list(self):
        """빈 리스트는 빈 리스트 반환"""
        # When
        result = news_engine.sort_articles_by_date([])
        
        # Then
        assert result == []
