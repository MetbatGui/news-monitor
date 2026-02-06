import asyncio
from datetime import datetime
from typing import Set
import logging

from core import Config
from domain.model import Article
from infrastructure.news.dto import ArticleData
from domain.ports.news_port import NewsScraper
from domain.ports.storage_port import StorageRepository
from domain.ports.alert_port import AlertSystem

# 순수 함수 import (테스트 용이)
from domain.logic import monitor_policy
from domain.logic import news_engine

logger = logging.getLogger(__name__)

class MonitorService:
    """모니터링 서비스 (Orchestrator)
    
    이 서비스는 순수한 비즈니스 로직(policy, engine)과
    부작용을 가진 작업(Repository, AlertSystem)을 조율합니다.
    """
    
    def __init__(
        self,
        news_repo: NewsRepository,
        storage_repo: StorageRepository,
        alert_system: AlertSystem
    ):
        self.news_repo = news_repo
        self.storage_repo = storage_repo
        self.alert_system = alert_system
        self.seen_ids: Set[int] = set()
        self.seen_links: Set[str] = set()
        self._last_check_date: str | None = None


    async def fetch_all_keywords(self, keywords: list[str]) -> list[Article]:
        """여러 키워드에 대해 기사를 수집하고 도메인 객체로 반환 (UI용)"""
        all_articles = []
        
        # keywords가 비어있으면 조기 리턴
        if not keywords:
            return []

        logger.debug(f"키워드 {len(keywords)}개 스캔 시작")
        
        # NewsRepositoryImpl이 내부적으로 병렬 처리를 수행하더라도, 
        # 여기서는 각 키워드별 호출을 비동기로 처리하여 응답성을 높임
        # NewsRepository.fetch_reports는 동기 메서드이므로 to_thread 사용
        
        tasks = []
        for keyword in keywords:
            tasks.append(asyncio.to_thread(self.news_repo.fetch_reports, keyword))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"키워드 '{keywords[i]}' 수집 중 오류: {result}")
                continue
                
            # ArticleData List -> Article List 변환
            for data in result:
                try:
                    article = self._create_article(data)
                    all_articles.append(article)
                except Exception as e:
                    logger.error(f"기사 데이터 변환 오류: {e}")

        return all_articles

    async def scan_once(self, keywords: list[str], notify: bool = True) -> list[Article]:
        """한 번의 스캔 사이클을 실행하고 새 기사를 반환"""
        # 1. 정책: 운영 시간 체크
        now = datetime.now()
        if not monitor_policy.is_work_time(now, Config.START_HOUR, Config.END_HOUR):
            logger.debug(f"운영 시간 외 ({now.strftime('%H:%M')})")
            pass

        # 2. 데이터 획득
        articles = await self.fetch_all_keywords(keywords)
        
        # 3. 중복 제거 및 알림
        new_articles = []
        for article in articles:
            # 중복 체크: Link(우선) + ID(보조)
            is_new = False
            link_str = str(article.link)
            
            if link_str in self.seen_links:
                is_new = False
            elif article.id and article.id != 0 and article.id in self.seen_ids:
                is_new = False
            else:
                is_new = True
            
            if is_new:
                if article.id:
                    self.seen_ids.add(article.id)
                self.seen_links.add(link_str)
                
                # 저장
                self.storage_repo.save_article(article)
                new_articles.append(article)

        # 일괄 알림 전송 (배치 처리)
        if notify and new_articles:
            self.alert_system.send_batch_notification(new_articles)

        return new_articles

    
    def _create_article(self, data: ArticleData) -> Article:
        """ArticleData DTO를 도메인 모델 Article로 변환
        
        Args:
            data: 어댑터가 반환한 원시 데이터
            
        Returns:
            검증된 도메인 모델 Article
        """
        return Article(
            id=data.id,
            title=data.title,
            link=data.link,
            date=data.date,
            keyword=data.keyword,
            source=data.source
        )
