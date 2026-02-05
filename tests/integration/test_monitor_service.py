
import asyncio
import sys
from pathlib import Path
import logging

# 프로젝트 루트 경로 추가
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root / "src"))

from application.services.monitor_service import MonitorService
from infrastructure.news.news_repository_impl import NewsRepositoryImpl
from infrastructure.storage.memory_storage_repository import MemoryStorageRepository
from domain.ports.alert_port import AlertSystem
from domain.model import Article

# 실제 스크래퍼 Import
from infrastructure.news.scrapers.rss.hankyung_rss_scraper import HankyungRssScraper
from infrastructure.news.scrapers.rss.etoday_rss_scraper import EtodayRssScraper

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DummyAlert(AlertSystem):
    def send_notification(self, article: Article) -> None:
        print(f"[알림 발생] {article.title}")

async def test_monitor_service_integration():
    print("=== MonitorService 통합 테스트 시작 ===")
    
    # 1. 의존성 준비 (테스트를 위해 가벼운 일부 스크래퍼만 사용)
    scrapers = [
        HankyungRssScraper(),
        EtodayRssScraper()
    ]
    news_repo = NewsRepositoryImpl(scrapers)
    storage_repo = MemoryStorageRepository()
    alert_system = DummyAlert() # 테스트용 알림
    
    service = MonitorService(news_repo, storage_repo, alert_system)
    
    # 2. fetch_all_keywords 테스트
    keywords = ["삼성전자", "반도체"]
    print(f"\n1. fetch_all_keywords(['삼성전자', '반도체']) 실행 중...")
    
    articles = await service.fetch_all_keywords(keywords)
    print(f"   -> 수집된 기사 수: {len(articles)}")
    if articles:
        print(f"   -> 샘플: {articles[0].title} ({articles[0].source})")
    
    # 3. scan_once 테스트 (알림 및 저장 로직 포함)
    print(f"\n2. scan_once(['삼성전자']) 실행 중...")
    new_articles = await service.scan_once(["삼성전자"], notify=True)
    
    print(f"   -> 새 기사 수: {len(new_articles)}")
    print(f"   -> 저장소 기사 수: {len(storage_repo.articles)}")
    print(f"   -> Seen IDs: {len(storage_repo.seen_ids)}")
    
    if len(new_articles) > 0:
        print("✅ scan_once 정상 동작 (새 기사 감지)")
    else:
        print("⚠️ 새 기사 없음 (정상일 수 있음)")
        
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    asyncio.run(test_monitor_service_integration())
