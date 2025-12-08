import webbrowser
import platform
from win11toast import toast as toast11
import win11toast
from domain.model import Article
import logging

logger = logging.getLogger(__name__)
from ports.alert_port import AlertSystem

# Monkeypatch win11toast.activated_args to fix TypeError with winrt
# The original code tries to call e.user_input(), but it's a property returning a ValueSet (not callable).
def patched_activated_args(_, event):
    try:
        from win11toast import ToastActivatedEventArgs
        e = ToastActivatedEventArgs._from(event)
        # We don't use user_input, so we can safely return empty dict
        # This avoids the buggy iteration/call on e.user_input
        return {
            'arguments': e.arguments,
            'user_input': {}
        }
    except Exception as e:
        logger.debug(f"활성화된 인자 패치 오류: {e}")
        return {'arguments': '', 'user_input': {}}

win11toast.activated_args = patched_activated_args

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
            logger.debug(f"토스트 알림 오류: {e}")
