from dataclasses import dataclass

@dataclass(frozen=True)
class Article:
    """뉴스 기사 정보를 담는 불변 객체"""
    id: int
    title: str
    link: str
    date: str
    keyword: str = ""
