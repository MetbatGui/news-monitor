import flet as ft
from typing import List, Callable
from infra.flet.components.keyword_manager import KeywordManager
from infra.flet.components.control_panel import ControlPanel
from infra.flet.components.article_card import ArticleCard
from infra.flet.components.status_bar import StatusBar
from domain.model import Article

from datetime import datetime, timedelta

class MainView(ft.Column):
    def __init__(self, on_start_stop: Callable[[bool], None], 
                 initial_keywords: List[str] = None,
                 initial_stock_names: List[str] = None,
                 on_keyword_change: Callable[[List[str], List[str]], None] = None):
        super().__init__()
        
        self.on_keyword_change = on_keyword_change
        
        self.keyword_manager = KeywordManager(
            label="키워드 추가", 
            initial_keywords=initial_keywords,
            on_change=lambda _: self._handle_change()
        )
        self.stock_manager = KeywordManager(
            label="종목명 추가", 
            initial_keywords=initial_stock_names,
            on_change=lambda _: self._handle_change()
        )
        self.control_panel = ControlPanel(on_start_stop=on_start_stop)
        self.status_bar = StatusBar()
        self.results_list = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=False)
        
        self.controls = [
            ft.Row(
                [
                    self.keyword_manager,
                    self.stock_manager,
                    self.control_panel
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            ft.Divider(),
            self.status_bar,
            self.results_list
        ]
        self.expand = True

    def _handle_change(self):
        if self.on_keyword_change:
            self.on_keyword_change(self.keyword_manager.keywords, self.stock_manager.keywords)

    def _is_recent(self, date_str: str) -> bool:
        try:
            # date_str format: "YYYY-MM-DD HH:MM"
            article_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            now = datetime.now()
            diff = now - article_date
            return diff <= timedelta(minutes=5)
        except Exception:
            return False

    async def set_articles(self, articles: List[Article]):
        self.results_list.controls.clear()
        for article in articles:
            is_highlighted = self._is_recent(article.date)
            self.results_list.controls.append(ArticleCard(article, is_highlighted=is_highlighted))
        self.results_list.update()

    def add_article(self, article: Article):
        self.results_list.controls.append(ArticleCard(article))
        self.results_list.update()

    def clear_results(self):
        self.results_list.controls.clear()
        self.results_list.update()

    async def update_status(self, msg: str):
        self.status_bar.update_status(msg)

    def get_keywords(self) -> List[str]:
        return self.keyword_manager.keywords

    def get_stock_names(self) -> List[str]:
        return self.stock_manager.keywords

    async def set_monitoring_state(self, is_monitoring: bool):
        self.control_panel.set_monitoring_state(is_monitoring)
