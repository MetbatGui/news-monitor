from typing import List
import logging
from domain.ports.alert_port import AlertSystem
from domain.model import Article

logger = logging.getLogger(__name__)

class CompositeAlertSystem(AlertSystem):
    """여러 AlertSystem을 묶어서 관리하는 Composite 클래스"""
    
    def __init__(self, alerts: List[AlertSystem]):
        self.alerts = alerts
        
    def add_alert_system(self, alert_system: AlertSystem):
        self.alerts.append(alert_system)
        
    def send_notification(self, article: Article) -> None:
        for alert in self.alerts:
            try:
                alert.send_notification(article)
            except Exception as e:
                logger.error(f"{type(alert).__name__} 알림 전송 실패: {e}", exc_info=True)

    def send_batch_notification(self, articles: List[Article]) -> None:
        if not articles:
            return
            
        for alert in self.alerts:
            try:
                alert.send_batch_notification(articles)
            except Exception as e:
                logger.error(f"{type(alert).__name__} 일괄 알림 전송 실패: {e}", exc_info=True)
