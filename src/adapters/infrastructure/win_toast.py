import webbrowser
import platform
from win11toast import toast as toast11
from domain.model import Article
from ports.alert_port import AlertSystem

class WinToast(AlertSystem):
    def __init__(self, on_click=None):
        self.on_click = on_click

    def send_notification(self, article: Article) -> None:
        try:
            # Use win11toast for all Windows versions (supports Win 10+)
            # If on_click is provided, use it. Otherwise default to opening the link.
            click_handler = (lambda args: self.on_click()) if self.on_click else (lambda args: webbrowser.open(article.link))
            
            toast11(
                "뉴스핌 리포트 모니터",
                article.title,
                on_click=click_handler,
                duration="short"
            )
        except Exception as e:
            print(f"Toast error: {e}")
