import threading
import time
import logging
import flet as ft
import pystray
from PIL import Image, ImageDraw
import win32gui
import win32con
from typing import Callable

logger = logging.getLogger(__name__)

class TrayIconManager:
    """시스템 트레이 아이콘 및 윈도우 복구 관리 클래스"""
    
    def __init__(self, page: ft.Page, on_exit: Callable):
        self.page = page
        self.on_app_exit = on_exit
        self.icon = None

    def setup_tray(self):
        """트레이 아이콘 설정 및 실행"""
        try:
            self.icon = pystray.Icon(
                "Newspim Monitor", 
                self._create_image(), 
                "Newspim Monitor", 
                menu=pystray.Menu(
                    pystray.MenuItem("Open", self._on_open),
                    pystray.MenuItem("Exit", self._on_exit_tray)
                )
            )
            
            threading.Thread(target=self._run_tray_loop, daemon=True).start()
            
        except Exception as e:
            logger.error(f"트레이 아이콘 설정 오류: {e}")

    def restore_window(self):
        """창을 전면으로 복구"""
        self.page.window_minimized = False
        self.page.window_visible = True
        self.page.update()
        
        try:
            hwnd = win32gui.FindWindow(None, "Newspim Monitor")
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            logger.debug(f"창 전면 표시 오류: {e}")

    def _create_image(self):
        try:
            width = 64
            height = 64
            color1 = "#2196F3"
            color2 = "white"
            image = Image.new('RGB', (width, height), color1)
            dc = ImageDraw.Draw(image)
            dc.rectangle(
                (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
                fill=color2)
            return image
        except Exception as e:
            logger.error(f"이미지 생성 오류: {e}")
            return None

    def _on_open(self, icon, item):
        self.restore_window()

    def _on_exit_tray(self, icon, item):
        if self.on_app_exit:
            self.on_app_exit()
        
        icon.stop()
        self.page.window_destroy()

    def _run_tray_loop(self):
        try:
            time.sleep(3) # Flet 초기화 대기
            logger.debug("트레이 아이콘 시작...")
            if self.icon.icon is None:
                self.icon.icon = self._create_image()
            self.icon.run()
        except Exception as e:
            logger.error(f"트레이 아이콘 실행 오류: {e}")
