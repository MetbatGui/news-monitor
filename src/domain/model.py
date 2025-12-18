from pydantic import BaseModel, HttpUrl, ConfigDict


class Article(BaseModel):
    """뉴스 기사 정보를 담는 불변 객체"""
    model_config = ConfigDict(frozen=True)

    id: int
    title: str
    link: HttpUrl
    date: str
    keyword: str = ""
    source: str = ""  # 뉴스 출처 (예: "이데일리", "연합뉴스")