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

from adapters.infrastructure.scrapers.web.newspim_scraper import NewspimScraper
from adapters.infrastructure.scrapers.web.edaily_scraper import EdailyScraper
from adapters.infrastructure.scrapers.web.hankyung_scraper import HankyungScraper
from adapters.infrastructure.scrapers.web.mk_scraper import MKScraper
from adapters.infrastructure.scrapers.web.mt_scraper import MTScraper
from adapters.infrastructure.scrapers.web.yonhap_scraper import YonhapScraper
from adapters.infrastructure.scrapers.web.asiae_scraper import AsiaeScraper
from adapters.infrastructure.scrapers.web.etoday_scraper import EtodayScraper
from adapters.infrastructure.scrapers.web.herald_scraper import HeraldScraper
from adapters.infrastructure.scrapers.web.seoul_scraper import SeoulScraper
from adapters.infrastructure.scrapers.web.fn_scraper import FnScraper
from adapters.infrastructure.scrapers.rss.infostock_scraper import InfostockScraper
from adapters.infrastructure.scrapers.rss.dart_rss_scraper import DartRssScraper
from adapters.infrastructure.keyword_storage import KeywordStorage
from adapters.infrastructure.win_toast import WinToast
from adapters.infrastructure.tts_service import TTSService
from infra.flet.views.main_view import MainView
from domain.model import Article
from config import DartConfig

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
        print(f"Image creation error: {e}")
        return None

def main(page: ft.Page):
    print("App started")
    page.title = "Newspim Monitor"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_prevent_close = True # Prevent app from closing on X click

    # State
    is_monitoring = False
    scrapers = [
        NewspimScraper(), 
        InfostockScraper(),
        DartRssScraper(DartConfig.RSS_URL)
    ]
    storage = KeywordStorage()
    tts = TTSService()
    
    # Load initial keywords
    initial_data = storage.load()
    initial_keywords = initial_data.get("keywords", [])
    initial_stock_names = initial_data.get("stock_names", [])

    def pre_generate_audio():
        print("Pre-generating audio for keywords...")
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
            print(f"Error forcing window to front: {e}")


    try:
        toaster = WinToast(on_click=restore_window)
    except Exception as e:
        print(f"WinToast init error: {e}")
        toaster = None
    
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
                print("Starting tray icon...")
                if icon.icon is None:
                    print("Icon image is None, regenerating...")
                    icon.icon = create_image()
                icon.run()
            except Exception as e:
                print(f"Tray icon run error: {e}")

        threading.Thread(target=run_tray, daemon=True).start()
    except Exception as e:
        print(f"Tray icon setup error: {e}")

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
                    print(f"Error generating audio for '{k}': {e}")
        
        threading.Thread(target=generate_audio_async, daemon=True).start()
        print(f"Saved keywords, generating TTS audio in background for {len(keywords + stock_names)} items...")
            
    view = MainView(
        on_start_stop=on_start_stop,
        initial_keywords=initial_data.get("keywords", []),
        initial_stock_names=initial_data.get("stock_names", []),
        on_keyword_change=on_keyword_change
    )
    page.add(view)
    
    async def monitor_loop():
        nonlocal is_monitoring
        all_articles = []
        current_links = set()
        
        # 스크래퍼 초기화
        scrapers = [
            NewspimScraper(),
            EdailyScraper(),
            HankyungScraper(),
            MKScraper(),
            MTScraper(),
            YonhapScraper(),
            AsiaeScraper(),
            EtodayScraper(),
            HeraldScraper(),
            SeoulScraper(),
            FnScraper(),
            InfostockScraper(),
            DartRssScraper()
        ]
        
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
            for term in search_terms:
                if not is_monitoring: break
                
                # 모든 스크래퍼를 병렬로 실행하여 베이스라인 수집
                tasks = [scraper.fetch_reports(term) for scraper in scrapers]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        print(f"Baseline fetch error: {result}")
                        continue
                    
                    articles = result
                    for article in articles:
                        current_links.add(article.link)
        except Exception as e:
            print(f"Baseline fetch error: {e}")
            
        await view.update_status(f"모니터링 시작... ({datetime.now().strftime('%H:%M:%S')}) - 새로운 기사 대기 중")

        while is_monitoring:
            keywords = view.get_keywords()
            stock_names = view.get_stock_names()
            search_terms = keywords + stock_names
            
            if not search_terms:
                 await view.update_status("키워드 또는 종목명을 추가해주세요.")
                 await view.set_monitoring_state(False)
                 break
            
            
            try:
                new_articles_this_cycle = []  # Track new articles in this cycle
                
                for term in search_terms:
                    if not is_monitoring: break
                    
                    # 모든 스크래퍼를 병렬로 실행
                    tasks = [scraper.fetch_reports(term) for scraper in scrapers]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # 결과 처리
                    for result in results:
                        if isinstance(result, Exception):
                            print(f"Scraper error: {result}")
                            continue
                        
                        articles = result
                        for article in articles:
                            if article.link not in current_links:
                                all_articles.append(article)
                                current_links.add(article.link)
                                new_articles_this_cycle.append((article, term))
                                
                                # Send notification
                                try:
                                    if toaster:
                                        toaster.send_notification(article)
                                except Exception as e:
                                    print(f"Notification error: {e}")
                
                # Group new articles by platform and play TTS
                if new_articles_this_cycle:
                    platform_groups = {}  # {platform_name: [keyword1, keyword2, ...]}
                    
                    for article, term in new_articles_this_cycle:
                        # article에서 source 사용 (스크래퍼가 이미 설정함)
                        source_name = article.source if article.source else "알 수 없음"
                            
                        if source_name not in platform_groups:
                            platform_groups[source_name] = []
                        platform_groups[source_name].append(term)
                    
                    # Play TTS: platform name once, then all keywords for that platform
                    for platform_name, keywords in platform_groups.items():
                        tts.play_sequence([platform_name] + keywords)
                    
                # Sort by date descending (newest first)
                all_articles.sort(key=lambda x: x.date, reverse=True)
                
                await view.set_articles(all_articles)
                await view.update_status(f"업데이트 완료 ({datetime.now().strftime('%H:%M:%S')}) - 총 {len(all_articles)}건")
                
            except Exception as e:
                await view.update_status(f"오류 발생: {str(e)}")
            
            # Wait for 60 seconds
            for _ in range(60):
                if not is_monitoring:
                    break
                await asyncio.sleep(1)
