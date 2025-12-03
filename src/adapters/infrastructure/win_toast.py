import webbrowser
from win11toast import toast
from domain.model import Article
from ports.alert_port import AlertSystem

class WinToast(AlertSystem):
    def __init__(self, on_click=None):
        self.on_click = on_click

    def send_notification(self, article: Article) -> None:
        try:
            # If on_click is provided, use it. Otherwise default to opening the link.
            click_handler = (lambda args: self.on_click()) if self.on_click else (lambda args: webbrowser.open(article.link))
            
            toast(
                "Newspim Report Monitor",
                article.title,
                on_click=click_handler,
                duration="short"
            )
        except Exception as e:
            print(f"Toast error: {e}")
