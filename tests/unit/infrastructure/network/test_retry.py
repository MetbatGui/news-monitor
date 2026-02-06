import pytest
from unittest.mock import Mock, patch
import httpx
from infrastructure.network.retry_utils import common_retry

# 테스트용 더미 클래스 및 메서드
class DummyClient:
    def __init__(self):
        self.call_count = 0

    @common_retry
    def fetch_something(self):
        self.call_count += 1
        # 1, 2번째 호출은 실패, 3번째 성공
        if self.call_count < 3:
            raise httpx.RequestError("Temporary failure")
        return "Success"
    
    @common_retry
    def fetch_always_fail(self):
        self.call_count += 1
        raise httpx.RequestError("Persistent failure")

def test_retry_eventually_succeeds():
    client = DummyClient()
    result = client.fetch_something()
    
    assert result == "Success"
    assert client.call_count == 3  # 3번 시도했는지 확인

def test_retry_fails_after_max_attempts():
    client = DummyClient()
    
    with pytest.raises(httpx.RequestError):
        client.fetch_always_fail()
        
    assert client.call_count == 3  # 최대 3번 시도 확인 (stop_after_attempt(3))
