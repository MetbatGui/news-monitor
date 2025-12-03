import flet as ft
import asyncio
import time
from datetime import datetime
from typing import List

from adapters.infrastructure.newspim_scraper import NewspimScraper
from infra.flet.views.main_view import MainView
from domain.model import Article

def main(page: ft.Page):
    page.title = "Newspim Monitor"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # State
    is_monitoring = False
    scraper = NewspimScraper()
    
    def on_start_stop(monitoring: bool):
        nonlocal is_monitoring
        is_monitoring = monitoring
        if is_monitoring:
            page.run_task(monitor_loop)
            
    view = MainView(on_start_stop=on_start_stop)
    page.add(view)
    
    async def monitor_loop():
        nonlocal is_monitoring
        while is_monitoring:
            keywords = view.get_keywords()
            stock_names = view.get_stock_names()
            search_terms = keywords + stock_names
            
            if not search_terms:
                 await view.update_status("키워드 또는 종목명을 추가해주세요.")
                 is_monitoring = False
                 await view.set_monitoring_state(False)
                 break
            
            all_articles = []
            
            await view.update_status(f"검색 중... ({datetime.now().strftime('%H:%M:%S')})")
            
            try:
                for term in search_terms:
                    if not is_monitoring: break
                    articles = await asyncio.to_thread(scraper.fetch_reports, term)
                    all_articles.extend(articles)
                    
                # Remove duplicates based on Link
                unique_articles = list({a.link: a for a in all_articles}.values())
                
                # Sort by date descending (newest first)
                unique_articles.sort(key=lambda x: x.date, reverse=True)
                
                await view.set_articles(unique_articles)
                await view.update_status(f"업데이트 완료 ({datetime.now().strftime('%H:%M:%S')}) - {len(unique_articles)}건 발견")
                
            except Exception as e:
                await view.update_status(f"오류 발생: {str(e)}")
            
            # Wait for 60 seconds
            for _ in range(60):
                if not is_monitoring:
                    break
                await asyncio.sleep(1)
