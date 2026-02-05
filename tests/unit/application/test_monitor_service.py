
import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch
from typing import List, Set

from application.services.monitor_service import MonitorService
from domain.model import Article
from infrastructure.news.dto import ArticleData
from domain.ports.news_port import NewsRepository
from domain.ports.storage_port import StorageRepository
from domain.ports.alert_port import AlertSystem
from core import Config

# --- Mock Implementations ---

class MockNewsRepository(NewsRepository):
    def __init__(self):
        self.mock_data = []
        
    def fetch_reports(self, keyword: str) -> List[ArticleData]:
        return self.mock_data

class MockStorageRepository(StorageRepository):
    def __init__(self):
        self.seen_ids = set()
        self.articles = []
        
    def load_today_ids(self) -> Set[int]:
        return self.seen_ids.copy()
        
    def save_article(self, article: Article) -> None:
        if article.id:
            self.seen_ids.add(article.id)
        self.articles.append(article)

class MockAlertSystem(AlertSystem):
    def __init__(self):
        self.sent_articles = []
        
    def send_notification(self, article: Article) -> None:
        self.sent_articles.append(article)

# --- Fixtures ---

@pytest.fixture
def mock_repos():
    news_repo = MockNewsRepository()
    storage_repo = MockStorageRepository()
    alert_system = MockAlertSystem()
    return news_repo, storage_repo, alert_system

@pytest.fixture
def monitor_service(mock_repos):
    news_repo, storage_repo, alert_system = mock_repos
    service = MonitorService(news_repo, storage_repo, alert_system)
    return service

# --- Tests ---

@pytest.mark.asyncio
async def test_scan_once_new_article(monitor_service, mock_repos):
    """새로운 기사가 발견되면 저장하고 알림을 보내야 한다."""
    news_repo, storage_repo, alert_system = mock_repos
    
    # Given
    article_data = ArticleData(
        id=100, title="New Article", link="http://test.com/1", 
        date="2024-01-01", keyword="test", source="Test"
    )
    news_repo.mock_data = [article_data]
    
    # When (운영 시간 강제 True 설정)
    with patch('domain.logic.monitor_policy.is_work_time', return_value=True):
        new_articles = await monitor_service.scan_once(["test"])
    
    # Then
    assert len(new_articles) == 1
    assert new_articles[0].id == 100
    assert 100 in storage_repo.seen_ids
    assert "http://test.com/1" in monitor_service.seen_links
    assert len(alert_system.sent_articles) == 1

@pytest.mark.asyncio
async def test_scan_once_duplicate_id(monitor_service, mock_repos):
    """이미 수집된 ID의 기사는 무시해야 한다."""
    news_repo, storage_repo, alert_system = mock_repos
    
    # Given: 이미 ID 100 수집됨
    monitor_service.seen_ids.add(100)
    
    article_data = ArticleData(
        id=100, title="New Article", link="http://test.com/1", 
        date="2024-01-01", keyword="test", source="Test"
    )
    news_repo.mock_data = [article_data]
    
    # When
    with patch('domain.logic.monitor_policy.is_work_time', return_value=True):
        new_articles = await monitor_service.scan_once(["test"])
    
    # Then
    assert len(new_articles) == 0
    assert len(alert_system.sent_articles) == 0

@pytest.mark.asyncio
async def test_scan_once_duplicate_link(monitor_service, mock_repos):
    """ID가 다르더라도 이미 수집된 Link의 기사는 무시해야 한다."""
    news_repo, storage_repo, alert_system = mock_repos
    
    # Given: 이미 해당 링크 수집됨
    monitor_service.seen_links.add("http://test.com/1")
    
    # ID는 새로운 200번이지만 링크가 같음
    article_data = ArticleData(
        id=200, title="Duplicate Link Article", link="http://test.com/1", 
        date="2024-01-01", keyword="test", source="Test"
    )
    news_repo.mock_data = [article_data]
    
    # When
    with patch('domain.logic.monitor_policy.is_work_time', return_value=True):
        new_articles = await monitor_service.scan_once(["test"])
    
    # Then
    assert len(new_articles) == 0
    assert len(alert_system.sent_articles) == 0

@pytest.mark.asyncio
async def test_fetch_all_keywords(monitor_service, mock_repos):
    """여러 키워드를 검색했을 때 결과를 합쳐야 한다."""
    news_repo, _, _ = mock_repos
    
    # Mock NewsRepository가 키워드에 따라 다른 결과를 주도록 설정은 복잡하므로
    # fetch_reports가 호출될 때마다 고정 데이터를 반환한다고 가정
    # (여기서는 단순 병합 로직 검증)
    
    data1 = ArticleData(id=1, title="A", link="http://test.com/1", date="d", keyword="k1", source="s")
    news_repo.mock_data = [data1]
    
    # When
    # 실제 구현에서 NewsRepository.fetch_reports를 호출함.
    # MockNewsRepository.fetch_reports는 항상 mock_data 반환.
    articles = await monitor_service.fetch_all_keywords(["k1", "k2"])
    
    # Then
    # k1 -> 1개, k2 -> 1개 => 총 2개
    assert len(articles) == 2
    assert articles[0].title == "A"
    assert articles[1].title == "A"

@pytest.mark.asyncio
async def test_work_time_policy(monitor_service):
    """운영 시간이 아니면 스캔을 건너뛰어야 한다."""
    
    # When: is_work_time -> False
    with patch('domain.logic.monitor_policy.is_work_time', return_value=False):
        new_articles = await monitor_service.scan_once(["test"])
        
    # Then
    assert len(new_articles) == 0
