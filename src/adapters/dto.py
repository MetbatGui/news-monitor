"""어댑터 레이어의 DTO (Data Transfer Object)"""
from dataclasses import dataclass


@dataclass
class ArticleData:
    """어댑터가 반환하는 원시 기사 데이터
    
    도메인 모델(Article)과 분리하여 어댑터 레이어의 책임을 명확히 함.
    서비스 레이어에서 이 DTO를 도메인 모델로 변환한다.
    """
    id: int
    title: str
    link: str
    date: str
    keyword: str = ""
    source: str = ""
