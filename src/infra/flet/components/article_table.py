import flet as ft
import webbrowser
from typing import List
from domain.model import Article


class ArticleTable(ft.Column):
    """기사 목록을 테이블 형태로 표시하는 컴포넌트"""
    
    def __init__(self):
        super().__init__()
        self.spacing = 0
        self.expand = True
        
        # DataTable 생성
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text("출처", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    numeric=False,
                ),
                ft.DataColumn(
                    ft.Text("제목", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    numeric=False,
                ),
                ft.DataColumn(
                    ft.Text("키워드", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    numeric=False,
                ),
                ft.DataColumn(
                    ft.Text("날짜", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    numeric=False,
                ),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            heading_row_color=ft.Colors.GREY_200,
            heading_row_height=50,
            data_row_min_height=60,
            data_row_max_height=100,
            column_spacing=30,
            width=1400,  # 테이블 너비 설정
        )
        
        # 스크롤 가능한 컨테이너로 감싸기 (중앙정렬)
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [self.data_table],
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # 중앙정렬
                    expand=True,
                ),
                alignment=ft.alignment.top_center,  # 컨테이너 중앙정렬
                expand=True,
            )
        ]
    
    def set_articles(self, articles: List[Article], highlighted_links: set = None):
        """기사 목록을 테이블에 표시"""
        self.data_table.rows.clear()
        
        if highlighted_links is None:
            highlighted_links = set()
        
        for article in articles:
            # 출처 판단
            source = self._get_source_name(article.link)
            
            # 하이라이트 여부
            is_highlighted = article.link in highlighted_links
            bg_color = ft.Colors.YELLOW_50 if is_highlighted else None
            
            # DataRow 생성
            row = ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                source, 
                                size=13, 
                                weight=ft.FontWeight.W500,
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=8,
                            alignment=ft.alignment.center,
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                article.title,
                                size=14,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                text_align=ft.TextAlign.LEFT,
                            ),
                            padding=8,
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                article.keyword if article.keyword else "-",
                                size=12,
                                color=ft.Colors.BLUE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            padding=8,
                            alignment=ft.alignment.center,
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                article.date, 
                                size=12,
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=8,
                            alignment=ft.alignment.center,
                        )
                    ),
                ],
                on_select_changed=lambda e, link=article.link: webbrowser.open(link),
                color=bg_color,
            )
            
            self.data_table.rows.append(row)
    
    def _get_source_name(self, link: str) -> str:
        """링크로 출처 판단"""
        if "newspim" in link:
            return "뉴스핌"
        elif "infostockdaily" in link:
            return "인포스탁"
        elif "dart.fss.or.kr" in link:
            return "DART"
        else:
            return "알 수 없음"
