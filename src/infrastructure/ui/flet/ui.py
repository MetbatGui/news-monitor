import flet as ft
import asyncio
from datetime import datetime
from typing import List
import logging

from infrastructure.storage.keyword_storage import KeywordStorage
from infrastructure.alerts.win_toast import WinToast
from infrastructure.alerts.tts_service import TTSService
from infrastructure.ui.flet.views.main_view import MainView
from application.services.monitor_service import MonitorService

# New Components
from infrastructure.ui.flet.tray_manager import TrayIconManager
from infrastructure.ui.flet.audio_generator import BackgroundAudioGenerator

logger = logging.getLogger(__name__)

def main(page: ft.Page, monitor_service: MonitorService, win_toast: WinToast, tts_service: TTSService):
    logger.info("앱 시작")
    page.title = "Newspim Monitor"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_prevent_close = True 

    # State
    is_monitoring = False
    
    # Dependencies
    storage = KeywordStorage()
    audio_generator = BackgroundAudioGenerator(tts_service)
    
    # 1. Setup Audio
    initial_data = storage.load()
    initial_keywords = initial_data.get("keywords", [])
    initial_stock_names = initial_data.get("stock_names", [])
    
    audio_generator.pre_generate_initial_audio(initial_keywords + initial_stock_names)
    
    # 2. Setup Tray & Window Management
    def on_app_exit():
        nonlocal is_monitoring
        is_monitoring = False
        
    tray_manager = TrayIconManager(page, on_exit=on_app_exit)
    tray_manager.setup_tray()
    
    if win_toast:
        win_toast.on_click = tray_manager.restore_window
        
    # Window Event Handler
    def on_window_event(e):
        if e.data == "close":
            page.window_visible = False
            page.update()

    page.on_window_event = on_window_event

    # 3. View Logic
    def on_start_stop(monitoring: bool):
        nonlocal is_monitoring
        is_monitoring = monitoring
        if is_monitoring:
            page.run_task(monitor_loop)
            
    def on_keyword_change(keywords: List[str], stock_names: List[str]):
        storage.save(keywords, stock_names)
        audio_generator.generate_for_new_keywords(keywords + stock_names)
            
    view = MainView(
        on_start_stop=on_start_stop,
        initial_keywords=initial_keywords,
        initial_stock_names=initial_stock_names,
        on_keyword_change=on_keyword_change
    )
    page.add(view)
    
    # 4. Monitor Loop
    async def monitor_loop():
        nonlocal is_monitoring
        display_articles = []
        
        # Baseline fetch setup
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
            await monitor_service.scan_once(search_terms, notify=False)
            await view.update_status(f"모니터링 시작... ({datetime.now().strftime('%H:%M:%S')}) - 새로운 기사 대기 중")
        except Exception as e:
            logger.error(f"베이스라인 가져오기 오류: {e}")
            await view.update_status(f"초기화 오류: {e}")

        while is_monitoring:
            loop_start_time = asyncio.get_running_loop().time()
            
            # Dynamic keywords update
            keywords = view.get_keywords()
            stock_names = view.get_stock_names()
            search_terms = keywords + stock_names
            
            if not search_terms:
                 await view.update_status("키워드 또는 종목명을 추가해주세요.")
                 await view.set_monitoring_state(False)
                 break
            
            try:
                new_articles = await monitor_service.scan_once(search_terms, notify=True)
                
                if new_articles:
                    logger.debug(f"새 기사 {len(new_articles)}개 발견")
                    display_articles.extend(new_articles)
                    
                    # UI 업데이트
                    await view.set_articles(display_articles)
                    
                    msg = f"업데이트 완료 ({datetime.now().strftime('%H:%M:%S')}) - 표시 {len(display_articles)}건 (신규 {len(new_articles)}건)"
                    await view.update_status(msg)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}", exc_info=True)
                await view.update_status(f"오류 발생: {str(e)}")
            
            # Drift Correction Logic
            elapsed = asyncio.get_running_loop().time() - loop_start_time
            wait_time = max(0, 60 - elapsed)
            
            logger.debug(f"작업 소요 시간: {elapsed:.2f}초, 대기 시간: {wait_time:.2f}초")
            
            end_wait_time = asyncio.get_running_loop().time() + wait_time
            while asyncio.get_running_loop().time() < end_wait_time:
                if not is_monitoring:
                    break
                # 0.5초 단위로 sleep하며 is_monitoring 체크
                await asyncio.sleep(min(0.5, end_wait_time - asyncio.get_running_loop().time()))
