import flet as ft
from infrastructure.ui.flet.ui import main
from config.logging_config import setup_logging

from infrastructure.news.scraper_factory import ScraperFactory
from infrastructure.news.news_repository_impl import NewsRepositoryImpl
from infrastructure.storage.memory_storage_repository import MemoryStorageRepository
from infrastructure.alerts.win_toast import WinToast
from infrastructure.alerts.tts_service import TTSService
from infrastructure.alerts.tts_alert_system import TTSAlertSystem
from infrastructure.alerts.composite_alert_system import CompositeAlertSystem
from application.services.monitor_service import MonitorService

if __name__ == "__main__":
    # 로깅 시스템 초기화
    setup_logging(log_level="INFO", log_dir="logs")
    
    # Flet 앱 시작
    # 의존성 주입 (Dependency Injection)
    
    # 1. Scrapers (Repository)
    scrapers = ScraperFactory.create_all_scrapers()
    news_repo = NewsRepositoryImpl(scrapers)
    
    # 2. Storage
    storage_repo = MemoryStorageRepository()
    
    # 3. Alert System Composition
    # WinToast (UI 콜백은 나중에 설정)
    win_toast = WinToast()
    
    # TTS Service & Alert System
    tts_service = TTSService()
    tts_alert = TTSAlertSystem(tts_service)
    
    # Composite Alert System
    alert_system = CompositeAlertSystem([win_toast, tts_alert])
    
    # 4. Service
    monitor_service = MonitorService(news_repo, storage_repo, alert_system)
    
    # Flet 앱 시작
    def app_main(page: ft.Page):
        # UI 메인 함수에 MonitorService와 WinToast(콜백 설정을 위해) 전달
        # 주의: ui.main 시그니처 변경 필요
        main(page, monitor_service, win_toast, tts_service)

    ft.app(target=app_main)