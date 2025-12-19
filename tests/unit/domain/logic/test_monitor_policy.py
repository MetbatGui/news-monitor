"""monitor_policy 순수 함수 테스트

이 테스트는 Mock 없이 순수 함수의 입출력만 검증합니다.
"""

from datetime import datetime
import pytest

from domain.logic import monitor_policy


class TestIsWorkTime:
    """is_work_time 함수 테스트"""
    
    def test_within_work_hours(self):
        """운영 시간 내에 있을 때 True 반환"""
        # Given: 10:30 AM
        now = datetime(2025, 12, 19, 10, 30)
        
        # When
        result = monitor_policy.is_work_time(now, 9, 18)
        
        # Then
        assert result is True
    
    def test_before_work_hours(self):
        """운영 시간 전일 때 False 반환"""
        # Given: 8:30 AM
        now = datetime(2025, 12, 19, 8, 30)
        
        # When
        result = monitor_policy.is_work_time(now, 9, 18)
        
        # Then
        assert result is False
    
    def test_after_work_hours(self):
        """운영 시간 후일 때 False 반환"""
        # Given: 6:30 PM
        now = datetime(2025, 12, 19, 18, 30)
        
        # When
        result = monitor_policy.is_work_time(now, 9, 18)
        
        # Then
        assert result is False
    
    def test_at_start_boundary(self):
        """시작 시간 정각일 때 True 반환"""
        # Given: 9:00 AM
        now = datetime(2025, 12, 19, 9, 0)
        
        # When
        result = monitor_policy.is_work_time(now, 9, 18)
        
        # Then
        assert result is True
    
    def test_at_end_boundary(self):
        """종료 시간 정각일 때 False 반환 (범위에서 제외)"""
        # Given: 6:00 PM
        now = datetime(2025, 12, 19, 18, 0)
        
        # When
        result = monitor_policy.is_work_time(now, 9, 18)
        
        # Then
        assert result is False


class TestCheckDayChanged:
    """check_day_changed 함수 테스트"""
    
    def test_date_changed(self):
        """날짜가 변경되었을 때 True 반환"""
        # When
        result = monitor_policy.check_day_changed("2025-12-18", "2025-12-19")
        
        # Then
        assert result is True
    
    def test_date_not_changed(self):
        """날짜가 변경되지 않았을 때 False 반환"""
        # When
        result = monitor_policy.check_day_changed("2025-12-19", "2025-12-19")
        
        # Then
        assert result is False
    
    def test_month_changed(self):
        """월이 변경되었을 때 True 반환"""
        # When
        result = monitor_policy.check_day_changed("2025-11-30", "2025-12-01")
        
        # Then
        assert result is True


class TestGetDateString:
    """get_date_string 함수 테스트"""
    
    def test_format_date(self):
        """datetime을 YYYY-MM-DD 형식으로 변환"""
        # Given
        dt = datetime(2025, 12, 19, 10, 30, 45)
        
        # When
        result = monitor_policy.get_date_string(dt)
        
        # Then
        assert result == "2025-12-19"
    
    def test_format_date_with_single_digit_month(self):
        """한 자리 월도 올바르게 포맷"""
        # Given
        dt = datetime(2025, 1, 5, 10, 30)
        
        # When
        result = monitor_policy.get_date_string(dt)
        
        # Then
        assert result == "2025-01-05"
