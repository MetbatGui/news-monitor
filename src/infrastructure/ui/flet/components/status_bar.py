import flet as ft

class StatusBar(ft.Text):
    def __init__(self):
        super().__init__(value="대기 중...", color=ft.Colors.GREY)
        
    def update_status(self, msg: str):
        self.value = msg
        self.update()
