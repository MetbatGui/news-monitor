import webbrowser
from win11toast import toast
from src.domain.model import Article
from src.ports.alert_port import AlertSystem

class WinToast(AlertSystem):
    def send_notification(self, article: Article) -> None:
        try:
            toast(
                "Newspim Report Monitor",
                article.title,
                on_click=lambda args: webbrowser.open(article.link),
                duration="short"
            )
        except Exception as e:
            print(f"Toast error: {e}")
