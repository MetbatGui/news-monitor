import flet as ft
import asyncio
import time
from datetime import datetime
from typing import List
import threading
import pystray
from PIL import Image, ImageDraw

from adapters.infrastructure.newspim_scraper import NewspimScraper
from adapters.infrastructure.keyword_storage import KeywordStorage
from adapters.infrastructure.win_toast import WinToast
from infra.flet.views.main_view import MainView
from domain.model import Article

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
    scraper = NewspimScraper()
    storage = KeywordStorage()
    
    def restore_window():
        page.window_minimized = False
        page.window_visible = True
        # Force window to front using always_on_top trick
        page.window_always_on_top = True
        page.update()
        page.window_always_on_top = False
        page.update()


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
        storage.save(keywords, stock_names)
            
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
                articles = await asyncio.to_thread(scraper.fetch_reports, term)
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
                for term in search_terms:
                    if not is_monitoring: break
                    articles = await asyncio.to_thread(scraper.fetch_reports, term)
                    for article in articles:
                        if article.link not in current_links:
                            all_articles.append(article)
                            current_links.add(article.link)
                            # Send notification
                            try:
                                if toaster:
                                    toaster.send_notification(article)
                            except Exception as e:
                                print(f"Notification error: {e}")
                    
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
