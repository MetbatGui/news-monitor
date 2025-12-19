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
from domain.logic.monitor_policy import MonitorPolicy, OperatingHours
from domain.logic.news_engine import NewsEngine

logger = logging.getLogger(__name__)

class MonitorService:
    """모니터링 서비스 (Orchestrator)
    
    이 서비스는 순수한 비즈니스 로직(Policy, Engine)과
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
                # 작업 시간이 간격을 초과한 경우 즉시 다음 작업 수행 (혹은 약간의 텀)
                await asyncio.sleep(0)

    def _scan_process(self):
        """실제 크롤링 및 알림 처리를 수행하는 동기 메서드
        
        이 메서드는 다음 순서로 동작합니다:
        1. 정책: 날짜 변경 감지 및 캐시 초기화
        2. 정책: 운영 시간 체크
        3. 데이터 획득: 기사 목록 조회
        4. 엔진: 새 기사 필터링
        5. 실행: 알림 발송 및 저장
        """
        now = datetime.now()
        today_str = MonitorPolicy.get_date_string(now)
        
        # 1. 정책: 날짜 변경 체크
        if MonitorPolicy.is_date_changed(today_str, self._last_check_date):
            logger.info(f"날짜 변경: {self._last_check_date} -> {today_str}. 캐시 초기화")
            self.seen_ids.clear()
            self._last_check_date = today_str
        elif self._last_check_date is None:
            # 초기 실행 시
            self._last_check_date = today_str
        
        # 2. 정책: 운영 시간 체크
        hours = OperatingHours(Config.START_HOUR, Config.END_HOUR)
        if not MonitorPolicy.is_operating_time(now, hours):
            logger.debug(f"운영 시간 외 ({now.strftime('%H:%M')})")
            return

        logger.debug(f"스캔 중... {now.strftime('%H:%M:%S')}")
        
        # 3. 데이터 획득: 기사 목록 조회 (불순 - 외부 시스템 호출)
        article_data_list = self.news_repo.fetch_reports(Config.KEYWORD)
        
        # 4. 엔진: 새 기사 필터링 (순수 함수)
        new_articles = NewsEngine.process_articles(
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
