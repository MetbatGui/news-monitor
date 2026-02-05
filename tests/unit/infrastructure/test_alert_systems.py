
import pytest
from unittest.mock import MagicMock, call
from domain.model import Article
from infrastructure.alerts.composite_alert_system import CompositeAlertSystem
from infrastructure.alerts.tts_alert_system import TTSAlertSystem
from infrastructure.alerts.tts_service import TTSService

class MockAlertSystem:
    def __init__(self):
        self.sent_articles = []
        self.batch_sent = False

    def send_notification(self, article):
        self.sent_articles.append(article)

    def send_batch_notification(self, articles):
        self.batch_sent = True
        for article in articles:
            self.send_notification(article)

def test_composite_alert_system_forwards_notifications():
    # Given
    alert1 = MockAlertSystem()
    alert2 = MockAlertSystem()
    composite = CompositeAlertSystem([alert1, alert2])
    
    article = Article(id=1, title="Test", link="http://example.com", date="date")
    
    # When
    composite.send_notification(article)
    
    # Then
    assert len(alert1.sent_articles) == 1
    assert len(alert2.sent_articles) == 1
    assert alert1.sent_articles[0] == article

def test_composite_alert_system_forwards_batch_notifications():
    # Given
    alert1 = MockAlertSystem()
    alert2 = MockAlertSystem()
    composite = CompositeAlertSystem([alert1, alert2])
    
    articles = [Article(id=1, title="Test", link="http://example.com", date="date")]
    
    # When
    composite.send_batch_notification(articles)
    
    # Then
    assert alert1.batch_sent is True
    assert alert2.batch_sent is True
    assert len(alert1.sent_articles) == 1

def test_tts_alert_system_batches_by_source():
    # Given
    mock_tts = MagicMock(spec=TTSService)
    tts_alert = TTSAlertSystem(mock_tts)
    
    articles = [
        Article(id=1, title="A1", link="http://example.com/1", date="d", source="NewsPim", keyword="K1"),
        Article(id=2, title="A2", link="http://example.com/2", date="d", source="NewsPim", keyword="K2"),
        Article(id=3, title="A3", link="http://example.com/3", date="d", source="Edaily", keyword="K3"),
    ]
    
    # When
    tts_alert.send_batch_notification(articles)
    
    # Then
    # Should call play_sequence twice (once for NewsPim, once for Edaily)
    # Order isn't guaranteed with dict, but calls should exist
    
    # Check calls
    # Expect: ["NewsPim", "K1", "K2"] and ["Edaily", "K3"]
    
    calls = mock_tts.play_sequence.call_args_list
    assert len(calls) == 2
    
    args_list = [c[0][0] for c in calls]
    
    # Sort inner lists for comparison if needed, or just check content
    # K1, K2 are for NewsPim
    newspim_call = next((args for args in args_list if args[0] == "NewsPim"), None)
    assert newspim_call is not None
    assert "K1" in newspim_call
    assert "K2" in newspim_call
    
    edaily_call = next((args for args in args_list if args[0] == "Edaily"), None)
    assert edaily_call is not None
    assert "K3" in edaily_call
