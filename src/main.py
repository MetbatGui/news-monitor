import flet as ft
from infra.flet.ui import main
from config.logging_config import setup_logging

from infrastructure.news.scrapers.rss.newspim_rss_scraper import NewspimRssScraper
from infrastructure.news.scrapers.rss.edaily_rss_scraper import EdailyRssScraper
from infrastructure.news.scrapers.rss.hankyung_rss_scraper import HankyungRssScraper
from infrastructure.news.scrapers.rss.mk_rss_scraper import MKRssScraper
from infrastructure.news.scrapers.web.mt_scraper import MTScraper
from infrastructure.news.scrapers.rss.yonhap_rss_scraper import YonhapRssScraper
from infrastructure.news.scrapers.rss.asiae_rss_scraper import AsiaeRssScraper
from infrastructure.news.scrapers.rss.etoday_rss_scraper import EtodayRssScraper
from infrastructure.news.scrapers.rss.herald_rss_scraper import HeraldRssScraper
from infrastructure.news.scrapers.rss.seoul_rss_scraper import SeoulRssScraper
from infrastructure.news.scrapers.web.fn_scraper import FnScraper
from infrastructure.news.scrapers.rss.infostock_scraper import InfostockScraper
from infrastructure.news.scrapers.rss.dart_rss_scraper import DartRssScraper

from infrastructure.news.news_repository_impl import NewsRepositoryImpl
from infrastructure.storage.memory_storage_repository import MemoryStorageRepository
from infrastructure.alerts.win_toast import WinToast
from application.services.monitor_service import MonitorService

if __name__ == "__main__":
    # 로깅 시스템 초기화
    setup_logging(log_level="INFO", log_dir="logs")
    
    # Flet 앱 시작
    # 의존성 주입 (Dependency Injection)
    # 1. Scrapers (Repository)
    scrapers = [
        NewspimRssScraper(),
        EdailyRssScraper(),
        HankyungRssScraper(),
        MKRssScraper(),
        MTScraper(),
        YonhapRssScraper(),
        AsiaeRssScraper(),
        EtodayRssScraper(),
        HeraldRssScraper(),
        SeoulRssScraper(),
        FnScraper(),
        InfostockScraper(),
        DartRssScraper()
    ]
    news_repo = NewsRepositoryImpl(scrapers)
    
    # 2. Storage & Alert
    storage_repo = MemoryStorageRepository()
    
    # AlertSystem은 UI(Windows Toast)에 의존하므로 ui.py 내부에서 생성되거나 여기서 생성해서 넘겨야 함
    # 하지만 WinToast는 콜백이 필요하므로 ui.py 내에서 생성되는게 자연스러움
    # 여기서는 임시로 None을 넘기고 ui.main 내부에서 설정하거나, 
    # ui.py가 MonitorService를 가지고 있으므로 ui.py 안에서 alert_system을 set 해주는 방식 등을 써야 함.
    # 하지만 MonitorService는 생성 시 AlertSystem을 요구함.
    # 따라서 WinToast를 여기서 생성하되, 콜백은 나중에 설정 가능한지 확인 필요.
    # WinToast 코드를 보면 __init__에서 on_click을 받음.
    
    # 해결책:
    # 1. UI 관련 라이브러리(win32gui 등)가 main.py 실행 시점에 문제 없는지 확인.
    # 2. WinToast를 여기서 생성하고, 콜백은 람다로 나중에 set 하거나,
    #    MonitorService 생성 시점에는 DummyAlert를 넣고 UI 초기화 시점에 교체 (Setter 필요)
    
    # 간단하게 가기 위해: WinToast를 여기서 생성 (콜백 없이 -> 기본 웹브라우저 오픈)
    alert_system = WinToast() 
    
    # 3. Service
    monitor_service = MonitorService(news_repo, storage_repo, alert_system)
    
    # Flet 앱 시작 (monitor_service 주입)
    # flet.app(target=main) 은 target에 page만 넘김. 커링(Currying) 필요.
    
    def app_main(page: ft.Page):
        # UI에서 WinToast 콜백 설정이 필요하다면 여기서 alert_system.on_click = ... 설정 가능
        main(page, monitor_service)

    ft.app(target=app_main)