import flet as ft
import threading
import time
import webbrowser
from datetime import datetime
from typing import List

from adapters.infrastructure.newspim_scraper import NewspimScraper
from domain.model import Article

def main(page: ft.Page):
    page.title = "Newspim Monitor"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # State
    is_monitoring = False
    scraper = NewspimScraper()
    
    # UI Components
    keyword_input = ft.TextField(label="검색 키워드 (Keyword)", width=200, value="AI")
    stock_name_input = ft.TextField(label="종목명 (Stock Name)", width=200)
    
    results_list = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=False)
    status_text = ft.Text(value="대기 중...", color=ft.Colors.GREY)
    
    def add_article_to_list(article: Article):
        # Create a card for each article
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ARTICLE),
                        ft.VerticalDivider(width=10, color=ft.Colors.TRANSPARENT),
                        ft.Text(article.title, weight=ft.FontWeight.BOLD, size=16, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                        ft.Column(
                            [
                                ft.Text("뉴스핌", size=12, color=ft.Colors.GREY),
                                ft.Text(article.date, size=12, color=ft.Colors.GREY)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=15,
                on_click=lambda _: webbrowser.open(article.link)
            )
        )

    def monitor_loop():
        nonlocal is_monitoring
        while is_monitoring:
            keyword = keyword_input.value
            if not keyword:
                page.run_task(update_status, "키워드를 입력해주세요.")
                is_monitoring = False
                page.run_task(update_button_state)
                break
                
            page.run_task(update_status, f"검색 중... ({datetime.now().strftime('%H:%M:%S')})")
            
            try:
                articles = scraper.fetch_reports(keyword)
                page.run_task(update_results, articles)
                page.run_task(update_status, f"업데이트 완료 ({datetime.now().strftime('%H:%M:%S')}) - {len(articles)}건 발견")
            except Exception as e:
                page.run_task(update_status, f"오류 발생: {str(e)}")
            
            # Wait for 60 seconds
            for _ in range(60):
                if not is_monitoring:
                    break
                time.sleep(1)

    async def update_status(msg):
        status_text.value = msg
        page.update()

    async def update_results(articles: List[Article]):
        results_list.controls.clear()
        for article in articles:
            results_list.controls.append(add_article_to_list(article))
        page.update()
        
    async def update_button_state():
        start_button.text = "모니터링 시작" if not is_monitoring else "모니터링 중지"
        start_button.icon = ft.Icons.PLAY_ARROW if not is_monitoring else ft.Icons.STOP
        keyword_input.disabled = is_monitoring
        stock_name_input.disabled = is_monitoring
        page.update()

    def toggle_monitoring(e):
        nonlocal is_monitoring
        if is_monitoring:
            is_monitoring = False
            status_text.value = "모니터링 중지됨"
        else:
            is_monitoring = True
            threading.Thread(target=monitor_loop, daemon=True).start()
            
        page.run_task(update_button_state)

    start_button = ft.ElevatedButton(
        text="모니터링 시작",
        icon=ft.Icons.PLAY_ARROW,
        on_click=toggle_monitoring
    )

    # Layout
    page.add(
        ft.Row(
            [
                keyword_input,
                stock_name_input,
                start_button
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        ft.Divider(),
        status_text,
        results_list
    )

ft.app(target=main)