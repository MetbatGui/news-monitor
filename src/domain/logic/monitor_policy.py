"""모니터링 정책 결정 로직 (순수 함수)"""

from datetime import datetime
from typing import NamedTuple


class OperatingHours(NamedTuple):
    """운영 시간 범위"""
    start_hour: int
    end_hour: int


class MonitorPolicy:
    """모니터링 정책 결정 (순수 함수 집합)
    
    이 클래스는 "언제 일할 것인가?"에 대한 정책 결정을 담당합니다.
    모든 메서드는 순수 함수로 구현되어 부작용이 없습니다.
    """
    
    @staticmethod
    def is_operating_time(now: datetime, hours: OperatingHours) -> bool:
        """운영 시간 여부 판단
        
        Args:
            now: 현재 시각
            hours: 운영 시간 범위
            
        Returns:
            운영 시간이면 True, 아니면 False
            
        Examples:
            >>> now = datetime(2025, 12, 19, 10, 30)
            >>> hours = OperatingHours(9, 18)
            >>> MonitorPolicy.is_operating_time(now, hours)
            True
        """
        return hours.start_hour <= now.hour < hours.end_hour
    
    @staticmethod
    def is_date_changed(current_date: str, last_date: str | None) -> bool:
        """날짜 변경 여부 판단
        
        Args:
            current_date: 현재 날짜 (YYYY-MM-DD 형식)
            last_date: 이전 체크 날짜 (None이면 초기 상태)
            
        Returns:
            날짜가 변경되었으면 True, 아니면 False
            
        Examples:
            >>> MonitorPolicy.is_date_changed("2025-12-19", "2025-12-18")
            True
            >>> MonitorPolicy.is_date_changed("2025-12-19", None)
            False
        """
        if last_date is None:
            return False
        return current_date != last_date
    
    @staticmethod
    def get_date_string(now: datetime) -> str:
        """datetime 객체를 YYYY-MM-DD 문자열로 변환
        
        Args:
            now: datetime 객체
            
        Returns:
            YYYY-MM-DD 형식의 날짜 문자열
        """
        return now.strftime("%Y-%m-%d")
