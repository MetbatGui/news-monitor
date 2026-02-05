import asyncio
from datetime import datetime
from typing import Set
import logging

from core import Config
from domain.model import Article
from infrastructure.news.dto import ArticleData
from domain.ports.news_port import NewsRepository
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

    async def run(self):
        """메인 감시 루프를 실행한다 (비동기)."""
        logger.info(f"모니터 서비스 시작 ({Config.START_HOUR}:00 ~ {Config.END_HOUR}:00)")
        
        # 초기화: 오늘 이미 수집한 기사 ID 로드
        self.seen_ids = self.storage_repo.load_today_ids()
        logger.info(f"저장된 ID {len(self.seen_ids)}개 로드 완료")

        while True:
            # 시작 시간 기록
            start_time = asyncio.get_running_loop().time()
            
            try:
                # 동기 작업인 스캔 로직을 별도 스레드에서 실행하여 이벤트 루프 차단 방지
                await asyncio.to_thread(self._scan_process)
            except Exception as e:
                logger.error(f"모니터 루프 오류: {e}", exc_info=True)
            
            # 경과 시간 계산 및 대기 (정확히 60초 간격 유지)
            elapsed = asyncio.get_running_loop().time() - start_time
            wait_time = max(0, Config.CHECK_INTERVAL - elapsed)
            
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(0)

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
                
                # 저장 및 알림
                self.storage_repo.save_article(article)
                
                if notify:
                    self.alert_system.send_notification(article)
                
                new_articles.append(article)

        return new_articles

    def _scan_process(self):
        """실제 크롤링 및 알림 처리를 수행하는 동기 메서드
        
        이 메서드는 다음 순서로 동작합니다:
        1. 정책: 날짜 변경 감지 및 캐시 초기화 (순수 함수)
        2. 정책: 운영 시간 체크 (순수 함수)
        3. 데이터 획득: 기사 목록 조회 (불순)
        4. 엔진: 새 기사 필터링 (순수 함수)
        5. 실행: 알림 발송 및 저장 (불순)
        """
        now = datetime.now()
        today_str = monitor_policy.get_date_string(now)
        
        # 1. 정책: 날짜 변경 체크 (순수 함수)
        if self._last_check_date and monitor_policy.check_day_changed(self._last_check_date, today_str):
            logger.info(f"날짜 변경: {self._last_check_date} -> {today_str}. 캐시 초기화")
            self.seen_ids.clear()
            self._last_check_date = today_str
        elif self._last_check_date is None:
            # 초기 실행 시
            self._last_check_date = today_str
        
        # 2. 정책: 운영 시간 체크 (순수 함수)
        if not monitor_policy.is_work_time(now, Config.START_HOUR, Config.END_HOUR):
            logger.debug(f"운영 시간 외 ({now.strftime('%H:%M')})")
            return

        logger.debug(f"스캔 중... {now.strftime('%H:%M:%S')}")
        
        # 3. 데이터 획득: 기사 목록 조회 (불순 - 외부 시스템 호출)
        article_data_list = self.news_repo.fetch_reports(Config.KEYWORD)
        
        # 4. 엔진: 새 기사 필터링 (순수 함수)
        new_articles = news_engine.process_articles(
            article_data_list,
            today_str,
            self.seen_ids
        )
        
        # 5. 실행: 알림 발송 및 저장 (불순)
        for article_data in new_articles:
            # ArticleData를 도메인 모델 Article로 변환
            article = self._create_article(article_data)
            
            logger.info(f"새 기사 발견: {article.title}")
            
            # 알림 발송
            self.alert_system.send_notification(article)
            
            # 저장
            self.storage_repo.save_article(article)
            
            # 메모리 업데이트
            self.seen_ids.add(article.id)
    
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
