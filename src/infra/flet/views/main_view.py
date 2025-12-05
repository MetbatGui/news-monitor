import flet as ft
from typing import List, Callable
from infra.flet.components.keyword_manager import KeywordManager
from infra.flet.components.control_panel import ControlPanel
from infra.flet.components.article_table import ArticleTable
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
        self.article_table = ArticleTable()
        
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
            self.article_table
        ]
        self.expand = True

    def _handle_change(self):
        if self.on_keyword_change:
            self.on_keyword_change(self.keyword_manager.keywords, self.stock_manager.keywords)

    def _get_recent_links(self, articles: List[Article]) -> set:
        """최근 5분 이내 기사 링크 반환"""
        recent_links = set()
        now = datetime.now()
        
        for article in articles:
            try:
                # date_str format: "YYYY-MM-DD HH:MM"
                article_date = datetime.strptime(article.date, "%Y-%m-%d %H:%M")
                diff = now - article_date
                if diff <= timedelta(minutes=5):
                    recent_links.add(article.link)
            except Exception:
                pass
        
        return recent_links

    async def set_articles(self, articles: List[Article]):
        # 정렬: 1. DART 우선, 2. 시간순 (최신순)
        def sort_key(article: Article):
            # DART 여부 판단
            is_dart = "dart.fss.or.kr" in article.link
            # DART면 1, 아니면 0 (reverse=True이므로 1이 먼저)
            source_priority = 1 if is_dart else 0
            # 시간은 역순 (최신이 먼저)
            return (source_priority, article.date)
        
        sorted_articles = sorted(articles, key=sort_key, reverse=True)
        
        highlighted_links = self._get_recent_links(sorted_articles)
        self.article_table.set_articles(sorted_articles, highlighted_links)
        self.article_table.update()

    def clear_results(self):
        self.article_table.set_articles([])
        self.article_table.update()

    async def update_status(self, msg: str):
        self.status_bar.update_status(msg)

    def get_keywords(self) -> List[str]:
        return self.keyword_manager.keywords

    def get_stock_names(self) -> List[str]:
        return self.stock_manager.keywords

    async def set_monitoring_state(self, is_monitoring: bool):
        self.control_panel.set_monitoring_state(is_monitoring)

