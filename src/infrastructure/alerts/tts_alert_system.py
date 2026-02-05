from typing import List, Dict
from domain.ports.alert_port import AlertSystem
from domain.model import Article
from infrastructure.alerts.tts_service import TTSService

class TTSAlertSystem(AlertSystem):
    """TTS를 이용한 알림 시스템"""
    
    def __init__(self, tts_service: TTSService):
        self.tts_service = tts_service
        
    def send_notification(self, article: Article) -> None:
        # 개별 알림은 단순히 제목을 읽거나 키워드를 읽는 등 정책에 따라 구현
        # 여기서는 간단히 "소스: 키워드" 형태로 읽음
        term = article.keyword if article.keyword else "키워드 없음"
        source = article.source if article.source else "출처 미상"
        self.tts_service.play_sequence([source, term])

    def send_batch_notification(self, articles: List[Article]) -> None:
        """여러 기사를 소스별로 그룹화하여 TTS 재생"""
        if not articles:
            return
            
        platform_groups: Dict[str, List[str]] = {}
        
        for article in articles:
            term = article.keyword if article.keyword else "알 수 없음"
            source_name = article.source if article.source else "알 수 없음"
            
            if source_name not in platform_groups:
                platform_groups[source_name] = []
            platform_groups[source_name].append(term)
        
        # 순차적으로 재생 요청
        for platform_name, keywords in platform_groups.items():
            # "뉴스핌: 삼성전자, SK하이닉스" 와 같이 읽도록 시퀀스 생성
            self.tts_service.play_sequence([platform_name] + keywords)
