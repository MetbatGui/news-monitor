"""모니터링 정책 결정 로직 (순수 함수)

이 모듈은 "언제 일할 것인가?"에 대한 정책 결정을 담당합니다.
모든 함수는 순수 함수로 구현되어 부작용이 없습니다.
"""

from datetime import datetime


def is_work_time(current_time: datetime, start_hour: int, end_hour: int) -> bool:
    """현재 시간이 운영 시간 범위 내에 있는지 판단 (순수 함수)
    
    Args:
        current_time: 현재 시각
        start_hour: 시작 시간 (0-23)
        end_hour: 종료 시간 (0-23)
        
    Returns:
        운영 시간이면 True, 아니면 False
        
    Examples:
        >>> now = datetime(2025, 12, 19, 10, 30)
        >>> is_work_time(now, 9, 18)
        True
        >>> is_work_time(now, 14, 18)
        False
    """
    return start_hour <= current_time.hour < end_hour


def check_day_changed(last_date: str, current_date: str) -> bool:
    """날짜가 변경되었는지 확인 (순수 함수)
    
    Args:
        last_date: 이전 체크 날짜 (YYYY-MM-DD 형식)
        current_date: 현재 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        날짜가 변경되었으면 True, 아니면 False
        
    Examples:
        >>> check_day_changed("2025-12-18", "2025-12-19")
        True
        >>> check_day_changed("2025-12-19", "2025-12-19")
        False
    """
    return last_date != current_date


def get_date_string(dt: datetime) -> str:
    """datetime 객체를 YYYY-MM-DD 문자열로 변환 (순수 함수)
    
    Args:
        dt: datetime 객체
        
    Returns:
        YYYY-MM-DD 형식의 날짜 문자열
        
    Examples:
        >>> dt = datetime(2025, 12, 19, 10, 30)
        >>> get_date_string(dt)
        '2025-12-19'
    """
    return dt.strftime("%Y-%m-%d")
