from abc import ABC, abstractmethod
from domain.model import Article

class AlertSystem(ABC):
    @abstractmethod
    def send_notification(self, article: Article) -> None:
        """사용자에게 알림을 보낸다."""
        pass
