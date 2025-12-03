import flet as ft
import webbrowser
from domain.model import Article

class ArticleCard(ft.Card):
    def __init__(self, article: Article, is_highlighted: bool = False):
        super().__init__()
        self.article = article
        self.color = ft.Colors.YELLOW_50 if is_highlighted else None
        self.content = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ARTICLE),
                    ft.VerticalDivider(width=10, color=ft.Colors.TRANSPARENT),
                    ft.Text(
                        article.title, 
                        weight=ft.FontWeight.BOLD, 
                        size=16, 
                        max_lines=2, 
                        overflow=ft.TextOverflow.ELLIPSIS, 
                        expand=True
                    ),
                    ft.Column(
                        [
                            ft.Text("뉴스핌", size=12, color=ft.Colors.GREY),
                            ft.Text(article.date, size=12, color=ft.Colors.GREY),
                            ft.Container(
                                content=ft.Text(article.keyword, size=12, color=ft.Colors.BLUE),
                                visible=bool(article.keyword)
                            )
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
