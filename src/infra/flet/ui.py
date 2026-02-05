import flet as ft
import asyncio
import time
from datetime import datetime
from typing import List
import threading
import pystray
from PIL import Image, ImageDraw
import win32gui
import win32con
import logging

from infrastructure.news.scrapers.web.mt_scraper import MTScraper
from infrastructure.news.scrapers.web.fn_scraper import FnScraper
from infrastructure.news.scrapers.rss.newspim_rss_scraper import NewspimRssScraper
from infrastructure.news.scrapers.rss.edaily_rss_scraper import EdailyRssScraper
from infrastructure.news.scrapers.rss.hankyung_rss_scraper import HankyungRssScraper
from infrastructure.news.scrapers.rss.mk_rss_scraper import MKRssScraper
from infrastructure.news.scrapers.rss.yonhap_rss_scraper import YonhapRssScraper
from infrastructure.news.scrapers.rss.asiae_rss_scraper import AsiaeRssScraper
from infrastructure.news.scrapers.rss.etoday_rss_scraper import EtodayRssScraper
from infrastructure.news.scrapers.rss.herald_rss_scraper import HeraldRssScraper
from infrastructure.news.scrapers.rss.seoul_rss_scraper import SeoulRssScraper  # lxml recover 모드로 수정
from infrastructure.news.scrapers.rss.infostock_scraper import InfostockScraper
from infrastructure.news.scrapers.rss.dart_rss_scraper import DartRssScraper
from infrastructure.storage.keyword_storage import KeywordStorage
from infrastructure.alerts.win_toast import WinToast
from infrastructure.alerts.tts_service import TTSService
from infra.flet.views.main_view import MainView
from domain.model import Article
from core.config import DartConfig

logger = logging.getLogger(__name__)

def create_image():
    try:
        # Generate an image for the tray icon
        width = 64
        height = 64
        color1 = "#2196F3" # Blue
        color2 = "white"
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
            fill=color2)
        return image
    except Exception as e:
        logger.error(f"이미지 생성 오류: {e}")
        return None

from application.services.monitor_service import MonitorService

from infrastructure.alerts.win_toast import WinToast
from infrastructure.alerts.tts_service import TTSService

def main(page: ft.Page, monitor_service: MonitorService, win_toast: WinToast, tts_service: TTSService):
    logger.info("앱 시작")
    page.title = "Newspim Monitor"
    page.padding = 20

    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_prevent_close = True # Prevent app from closing on X click

    # State
    is_monitoring = False
    
    # Scrapers & Storage는 main.py에서 생성되어 news_repository_impl에 주입됨.
    # 여기서는 키워드 스토리지 로드용으로만 새로 생성하거나, main.py에서 넘겨받아야 함.
    # 하지만 기존 코드는 여기서 KeywordStorage를 생성함. (유지)
    storage = KeywordStorage()
    
    # TTSService는 주입받은 객체 사용
    tts = tts_service
    
    # Load initial keywords
    initial_data = storage.load()
    initial_keywords = initial_data.get("keywords", [])
    initial_stock_names = initial_data.get("stock_names", [])

    def pre_generate_audio():
        logger.info("키워드 오디오 사전 생성 중...")
        # Pre-generate audio for sources
        tts.generate_audio("뉴스핌")
        tts.generate_audio("인포스탁")
        tts.generate_audio("DART")
        tts.generate_audio("이데일리")
        tts.generate_audio("한국경제")
        tts.generate_audio("매일경제")
        tts.generate_audio("머니투데이")
        tts.generate_audio("연합뉴스")
        tts.generate_audio("아시아경제")
        tts.generate_audio("이투데이")
        tts.generate_audio("헤럴드경제")
        tts.generate_audio("서울경제")
        tts.generate_audio("파이낸셜뉴스")
        
        for k in initial_keywords + initial_stock_names:
            tts.generate_audio(k)
            
    threading.Thread(target=pre_generate_audio, daemon=True).start()
    
    def restore_window():
        page.window_minimized = False
        page.window_visible = True
        page.update()
        
        try:
            hwnd = win32gui.FindWindow(None, "Newspim Monitor")
            if hwnd:
                # Force restore if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Force foreground
                win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            logger.debug(f"창 전면 표시 오류: {e}")

    # WinToast 콜백 설정 (주입받은 객체에 설정)
    if win_toast:
        win_toast.on_click = restore_window
    
    # Tray Icon Setup
    def on_open(icon, item):
        restore_window()

    def on_exit(icon, item):
        nonlocal is_monitoring
        is_monitoring = False
        icon.stop()
        page.window_destroy()

    try:
        icon = pystray.Icon("Newspim Monitor", create_image(), "Newspim Monitor", menu=pystray.Menu(
            pystray.MenuItem("Open", on_open),
            pystray.MenuItem("Exit", on_exit)
        ))

        def run_tray():
            try:
                time.sleep(3) # Wait for Flet to initialize
                logger.debug("트레이 아이콘 시작...")
                if icon.icon is None:
                    logger.debug("아이콘 이미지 없음, 재생성 중...")
                    icon.icon = create_image()
                icon.run()
            except Exception as e:
                logger.error(f"트레이 아이콘 실행 오류: {e}")

        threading.Thread(target=run_tray, daemon=True).start()
    except Exception as e:
        logger.error(f"트레이 아이콘 설정 오류: {e}")

    def on_window_event(e):
        if e.data == "close":
            page.window_visible = False
            page.update()

    page.on_window_event = on_window_event
    
    # Load initial keywords
    initial_data = storage.load()
    
    def on_start_stop(monitoring: bool):
        nonlocal is_monitoring
        is_monitoring = monitoring
        if is_monitoring:
            page.run_task(monitor_loop)
            
    def on_keyword_change(keywords: List[str], stock_names: List[str]):
        """키워드 변경 시 호출되는 콜백 함수
        
        - JSON 파일에 저장
        - TTS 오디오를 백그라운드 스레드에서 비동기 생성 (UI 차단 방지)
        """
        storage.save(keywords, stock_names)
        
        # TTS 오디오 생성을 백그라운드 스레드에서 실행하여 UI 딜레이 방지
        def generate_audio_async():
            for k in keywords + stock_names:
                try:
                    tts.generate_audio(k)
                except Exception as e:
                    logger.debug(f"'{k}' 오디오 생성 오류: {e}")
        
        threading.Thread(target=generate_audio_async, daemon=True).start()
        logger.info(f"키워드 저장 완료, {len(keywords + stock_names)}개 항목 TTS 오디오 백그라운드 생성 중...")
            
    view = MainView(
        on_start_stop=on_start_stop,
        initial_keywords=initial_data.get("keywords", []),
        initial_stock_names=initial_data.get("stock_names", []),
        on_keyword_change=on_keyword_change
    )
    page.add(view)
    
    async def monitor_loop():
        nonlocal is_monitoring
        
        # 화면에 표시할 기사 목록 (Baseline 제외, 신규 기사만 누적)
        display_articles = []
        
        # Baseline fetch - get current articles but don't display them
        keywords = view.get_keywords()
        stock_names = view.get_stock_names()
        search_terms = keywords + stock_names
        
        if not search_terms:
             await view.update_status("키워드 또는 종목명을 추가해주세요.")
             is_monitoring = False
             await view.set_monitoring_state(False)
             return

        await view.update_status("초기 데이터 수집 중... (화면에 표시되지 않음)")
        try:
            # Baseline: 알림 없이 데이터만 수집 (seen_ids 등록)
            # 여기서 반환된 articles는 이미 이전에 작성된 기사들이므로 화면에 표시하지 않음
            await monitor_service.scan_once(search_terms, notify=False)
            
            # Baseline 완료 후 화면 갱신 없이 상태 메시지만 업데이트
            await view.update_status(f"모니터링 시작... ({datetime.now().strftime('%H:%M:%S')}) - 새로운 기사 대기 중")
            
        except Exception as e:
            logger.error(f"베이스라인 가져오기 오류: {e}")
            await view.update_status(f"초기화 오류: {e}")

        while is_monitoring:
            # 루프 시작 시간 기록 (Drift 보정용)
            loop_start_time = asyncio.get_running_loop().time()
            
            keywords = view.get_keywords()
            stock_names = view.get_stock_names()
            search_terms = keywords + stock_names
            
            if not search_terms:
                 await view.update_status("키워드 또는 종목명을 추가해주세요.")
                 await view.set_monitoring_state(False)
                 break
            
            try:
                # MonitorService를 통해 데이터 수집 및 알림 처리(TTS, Toast 등)
                new_articles = await monitor_service.scan_once(search_terms, notify=True)
                
                if new_articles:
                    logger.debug(f"새 기사 {len(new_articles)}개 발견")
                    
                    # 화면 표시 목록에 추가
                    display_articles.extend(new_articles)
                    
                    # TTS 알림 처리는 MonitorService 내부의 AlertSystem이 담당하므로 제거됨

                # UI 업데이트 (누적된 display_articles 사용)
                # 최신순 정렬은 view._update_table에서 수행됨
                await view.set_articles(display_articles)
                
                msg = f"업데이트 완료 ({datetime.now().strftime('%H:%M:%S')}) - 표시 {len(display_articles)}건"
                if new_articles:
                    msg += f" (신규 {len(new_articles)}건)"
                await view.update_status(msg)

                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}", exc_info=True)
                await view.update_status(f"오류 발생: {str(e)}")
            
            # Wait with Drift Correction
            elapsed = asyncio.get_running_loop().time() - loop_start_time
            wait_time = max(0, 60 - elapsed)
            
            logger.debug(f"작업 소요 시간: {elapsed:.2f}초, 대기 시간: {wait_time:.2f}초")
            
            end_wait_time = asyncio.get_running_loop().time() + wait_time
            while asyncio.get_running_loop().time() < end_wait_time:
                if not is_monitoring:
                    break
                await asyncio.sleep(min(0.5, end_wait_time - asyncio.get_running_loop().time()))
