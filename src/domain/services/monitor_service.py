import asyncio
from datetime import datetime
from typing import Set
import logging

from config import Config
from ports.news_port import NewsRepository
from ports.storage_port import StorageRepository
from ports.alert_port import AlertSystem

logger = logging.getLogger(__name__)

class MonitorService:
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
        """실제 크롤링 및 알림 처리를 수행하는 동기 메서드"""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        
        # 날짜 변경 체크 및 캐시 초기화
        if not hasattr(self, '_last_check_date'):
            self._last_check_date = today_str
            
        if self._last_check_date != today_str:
            logger.info(f"날짜 변경: {self._last_check_date} -> {today_str}. 캐시 초기화")
            self.seen_ids.clear()
            self._last_check_date = today_str
        
        # 운영 시간 체크
        if not (Config.START_HOUR <= now.hour < Config.END_HOUR):
            logger.debug(f"운영 시간 외 ({now.strftime('%H:%M')})")
            return

        logger.debug(f"스캔 중... {now.strftime('%H:%M:%S')}")
        
        # 기사 조회
        articles = self.news_repo.fetch_reports(Config.KEYWORD)
        
        today_str = now.strftime("%Y-%m-%d")
        
        for article in articles:
            # 날짜 필터링: 오늘 작성된 기사만 처리
            # article.date 형식: "2025-12-02 10:22"
            if not article.date.startswith(today_str):
                continue

            if article.id not in self.seen_ids:
                logger.info(f"새 기사 발견: {article.title}")
                
                # 알림 발송
                self.alert_system.send_notification(article)
                
                # 저장
                self.storage_repo.save_article(article)
                
                # 메모리 업데이트
                self.seen_ids.add(article.id)
