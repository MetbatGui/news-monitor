import flet as ft
from typing import Callable

class ControlPanel(ft.Row):
    def __init__(self, on_start_stop: Callable[[bool], None] = None):
        super().__init__()
        self.on_start_stop = on_start_stop
        self.is_monitoring = False
        
        self.start_button = ft.ElevatedButton(
            text="모니터링 시작",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.toggle_monitoring
        )
        
        self.controls = [
            self.start_button
        ]
        self.alignment = ft.MainAxisAlignment.CENTER

    def toggle_monitoring(self, e):
        self.is_monitoring = not self.is_monitoring
        self.update_button_state()
        if self.on_start_stop:
            self.on_start_stop(self.is_monitoring)

    def update_button_state(self):
        self.start_button.text = "모니터링 중지" if self.is_monitoring else "모니터링 시작"
        self.start_button.icon = ft.Icons.STOP if self.is_monitoring else ft.Icons.PLAY_ARROW
        self.update()
        
    def set_monitoring_state(self, is_monitoring: bool):
        self.is_monitoring = is_monitoring
        self.update_button_state()
