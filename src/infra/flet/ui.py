import flet as ft
import asyncio
import time
from datetime import datetime
from typing import List

from adapters.infrastructure.newspim_scraper import NewspimScraper
from adapters.infrastructure.keyword_storage import KeywordStorage
from infra.flet.views.main_view import MainView
from domain.model import Article

def main(page: ft.Page):
    page.title = "Newspim Monitor"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # State
    is_monitoring = False
    scraper = NewspimScraper()
    storage = KeywordStorage()
    
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
                 is_monitoring = False
                 await view.set_monitoring_state(False)
                 break
            
            # Accumulate articles
            
            try:
                for term in search_terms:
                    if not is_monitoring: break
                    articles = await asyncio.to_thread(scraper.fetch_reports, term)
                    for article in articles:
                        if article.link not in current_links:
                            all_articles.append(article)
                            current_links.add(article.link)
                    
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
