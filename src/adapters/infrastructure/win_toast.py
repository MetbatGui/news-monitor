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
            # Check Windows version
            # Windows 11 is build 22000 or higher
            version_str = platform.version()
            build_number = int(version_str.split('.')[-1]) if '.' in version_str else 0
            is_win11 = build_number >= 22000

            if is_win11:
                # If on_click is provided, use it. Otherwise default to opening the link.
                click_handler = (lambda args: self.on_click()) if self.on_click else (lambda args: webbrowser.open(article.link))
                
                toast11(
                    "Newspim Report Monitor",
                    article.title,
                    on_click=click_handler,
                    duration="short"
                )
            else:
                # Windows 10 fallback using win10toast
                # Note: win10toast does not support on_click callbacks natively in the same way
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(
                    "Newspim Report Monitor",
                    article.title,
                    duration=5,
                    threaded=True
                )
        except Exception as e:
            print(f"Toast error: {e}")
