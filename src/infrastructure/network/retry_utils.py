from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx
import logging

logger = logging.getLogger(__name__)

def log_retry_attempt(retry_state):
    """재시도 로깅 콜백"""
    exception = retry_state.outcome.exception()
    logger.warning(
        f"요청 실패 (시도 {retry_state.attempt_number}): {exception}. "
        f"{retry_state.next_action.sleep}초 후 재시도..."
    )

# 공통 재시도 설정 (3회 재시도, 지수 백오프)
common_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException, ConnectionError)),
    before_sleep=log_retry_attempt,
    reraise=True
)
