from abc import ABC, abstractmethod
from domain.model import Article

class AlertSystem(ABC):
    @abstractmethod
    def send_notification(self, article: Article) -> None:
        """사용자에게 알림을 보낸다."""
        pass

    def send_batch_notification(self, articles: list[Article]) -> None:
        """여러 알림을 일괄 전송한다.
        기본 구현은 개별 알림을 순차적으로 호출한다.
        """
        for article in articles:
            self.send_notification(article)
