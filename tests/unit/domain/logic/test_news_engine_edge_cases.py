"""날짜 필터링 로직 테스트 (엣지 케이스)"""

import pytest
from domain.logic import news_engine
from infrastructure.news.dto import ArticleData


class TestFilterByDateEdgeCases:
    """날짜 필터링 엣지 케이스 테스트"""
    
    def test_empty_date_string(self):
        """빈 날짜 문자열은 필터링되어야 함"""
        # Given
        articles = [
            ArticleData(id=1, title="A", link="link1", date="", keyword="test", source="test"),
            ArticleData(id=2, title="B", link="link2", date="2025-12-19 10:00", keyword="test", source="test"),
        ]
        
        # When
        result = news_engine.filter_by_date(articles, "2025-12-19")
        
        # Then
        assert len(result) == 1
        assert result[0].id == 2
    
    def test_none_date(self):
        """None 날짜는 필터링되어야 함"""
        # Given
        articles = [
            ArticleData(id=1, title="A", link="link1", date=None, keyword="test", source="test"),
            ArticleData(id=2, title="B", link="link2", date="2025-12-19 10:00", keyword="test", source="test"),
        ]
        
        # When
        result = news_engine.filter_by_date(articles, "2025-12-19")
        
        # Then
        assert len(result) == 1
        assert result[0].id == 2
    
    def test_different_date_formats(self):
        """다양한 날짜 형식이 올바르게 필터링되는지 확인"""
        # Given
        articles = [
            ArticleData(id=1, title="A", link="link1", date="2025-12-19 10:00", keyword="test", source="test"),
            ArticleData(id=2, title="B", link="link2", date="2025-12-19", keyword="test", source="test"),
            ArticleData(id=3, title="C", link="link3", date="2025-12-18 15:00", keyword="test", source="test"),
            ArticleData(id=4, title="D", link="link4", date="2025.12.19 10:00", keyword="test", source="test"),  # 잘못된 형식
        ]
        
        # When
        result = news_engine.filter_by_date(articles, "2025-12-19")
        
        # Then
        assert len(result) == 2  # id=1, id=2만 통과
        assert {r.id for r in result} == {1, 2}
    
    def test_whitespace_only_date(self):
        """공백만 있는 날짜는 필터링되어야 함"""
        # Given
        articles = [
            ArticleData(id=1, title="A", link="link1", date="   ", keyword="test", source="test"),
            ArticleData(id=2, title="B", link="link2", date="2025-12-19 10:00", keyword="test", source="test"),
        ]
        
        # When
        result = news_engine.filter_by_date(articles, "2025-12-19")
        
        # Then
        assert len(result) == 1
        assert result[0].id == 2
