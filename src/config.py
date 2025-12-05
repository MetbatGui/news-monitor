class Config:
    START_HOUR = 7
    END_HOUR = 18
    CHECK_INTERVAL = 60  # seconds
    TARGET_URL = "https://www.newspim.com/search?searchword=리포트+브리핑"
    KEYWORD = "리포트 브리핑"


class DartConfig:
    """DART RSS 모니터링 설정"""
    RSS_URL = "https://dart.fss.or.kr/api/todayRSS.xml"
    
    # 모니터링할 카테고리 (빈 문자열이면 전체, 특정 카테고리면 필터링)
    # 옵션: "유가", "코스닥", "코넥스", "기타" 또는 ""
    CATEGORY_FILTER = ""  # 전체 모니터링 (알림 폭주 주의!)
