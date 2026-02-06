import flet as ft
from typing import List, Callable
from infrastructure.ui.flet.components.keyword_manager import KeywordManager
from infrastructure.ui.flet.components.control_panel import ControlPanel
from infrastructure.ui.flet.components.article_table import ArticleTable
from infrastructure.ui.flet.components.status_bar import StatusBar
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
        
        # 탭 필터 추가
        self.all_articles: List[Article] = []
        self.current_filter = "전체"
        
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            scrollable=True,
            on_change=self._handle_tab_change,
            tabs=[
                ft.Tab(text="전체"),
                ft.Tab(text="DART"),
                ft.Tab(text="인포스탁"),
                ft.Tab(text="뉴스핌"),
                ft.Tab(text="이데일리"),
                ft.Tab(text="한국경제"),
                ft.Tab(text="매일경제"),
                ft.Tab(text="머니투데이"),
                ft.Tab(text="연합뉴스"),
                ft.Tab(text="아시아경제"),
                ft.Tab(text="이투데이"),
                ft.Tab(text="헤럴드경제"),
                ft.Tab(text="서울경제"),
                ft.Tab(text="파이낸셜뉴스"),  # 수정: FnGuide -> 파이낸셜뉴스
            ]
        )
        
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
            self.tabs,  # 탭 추가
            self.status_bar,
            self.article_table
        ]
        self.expand = True

    def _handle_tab_change(self, e):
        """탭 변경 시 필터 업데이트 및 테이블 갱신"""
        self.current_filter = e.control.tabs[e.control.selected_index].text
        self._update_table()

    def _update_table(self):
        """현재 필터와 정렬 기준에 따라 테이블 업데이트"""
        # 1. 필터링
        if self.current_filter == "전체":
            filtered_articles = self.all_articles
        else:
            filtered_articles = [
                a for a in self.all_articles 
                if a.source == self.current_filter
            ]
            
        # 2. 정렬 (DART 우선 + 최신순)
        def sort_key(article: Article):
            # HttpUrl 객체이므로 문자열 변환 필요
            link_str = str(article.link)
            is_dart = "dart.fss.or.kr" in link_str
            source_priority = 1 if is_dart else 0
            return (source_priority, article.date)
        
        sorted_articles = sorted(filtered_articles, key=sort_key, reverse=True)
        
        # 3. 하이라이트 및 테이블 업데이트
        highlighted_links = self._get_recent_links(sorted_articles)
        self.article_table.set_articles(sorted_articles, highlighted_links)
        self.article_table.update()

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
                    recent_links.add(str(article.link))
            except Exception:
                pass
        
        return recent_links

    async def set_articles(self, articles: List[Article]):
        self.all_articles = articles
        self._update_table()

    def clear_results(self):
        self.all_articles = []
        self._update_table()

    async def update_status(self, msg: str):
        self.status_bar.update_status(msg)

    def get_keywords(self) -> List[str]:
        return self.keyword_manager.keywords

    def get_stock_names(self) -> List[str]:
        return self.stock_manager.keywords

    async def set_monitoring_state(self, is_monitoring: bool):
        self.control_panel.set_monitoring_state(is_monitoring)

