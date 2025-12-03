import flet as ft
from typing import List, Callable

class KeywordManager(ft.Column):
    def __init__(self, label: str = "키워드 추가", initial_keywords: List[str] = None, on_change: Callable[[List[str]], None] = None):
        super().__init__()
        self.keywords: List[str] = initial_keywords if initial_keywords else []
        self.on_change = on_change
        
        self.input_field = ft.TextField(
            label=label, 
            width=200, 
            on_submit=self.add_keyword
        )
        
        self.add_button = ft.IconButton(
            icon=ft.Icons.ADD, 
            on_click=self.add_keyword
        )
        
        self.chips_row = ft.Row(wrap=True, spacing=5)
        self.update_chips()
        
        self.controls = [
            ft.Row([self.input_field, self.add_button]),
            self.chips_row
        ]

    def add_keyword(self, e):
        keyword = self.input_field.value.strip()
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.input_field.value = ""
            self.update_chips()
            if self.on_change:
                self.on_change(self.keywords)
            self.update()

    def remove_keyword(self, keyword):
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            self.update_chips()
            if self.on_change:
                self.on_change(self.keywords)
            self.update()

    def update_chips(self):
        self.chips_row.controls = [
            ft.Chip(
                label=ft.Text(k),
                on_delete=lambda e, k=k: self.remove_keyword(k)
            ) for k in self.keywords
        ]
