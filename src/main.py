import flet as ft
from infra.flet.ui import main
from config.logging_config import setup_logging

if __name__ == "__main__":
    # 로깅 시스템 초기화
    setup_logging(log_level="INFO", log_dir="logs")
    
    # Flet 앱 시작
    ft.app(target=main)