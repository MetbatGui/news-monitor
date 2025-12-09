"""WinToast 알림 테스트"""
import sys
sys.path.insert(0, 'src')

from adapters.infrastructure.win_toast import WinToast
from domain.model import Article

print("WinToast 초기화 중...")
try:
    toaster = WinToast()
    print("✓ WinToast 초기화 성공!")
    
    # 테스트 아티클 생성
    test_article = Article(
        id=1,
        title="테스트 알림",
        link="https://example.com",
        date="2025-12-09 15:00",
        keyword="테스트",
        source="테스트"
    )
    
    print("\n알림 전송 중...")
    toaster.send_notification(test_article)
    print("✓ 알림 전송 완료!")
    print("\n알림이 나타났나요? (5초 대기)")
    
    import time
    time.sleep(5)
    
except Exception as e:
    print(f"✗ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
