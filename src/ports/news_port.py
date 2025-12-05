from abc import ABC, abstractmethod
from typing import List
from domain.model import Article

class NewsRepository(ABC):
    @abstractmethod
    async def fetch_reports(self, keyword: str) -> List[Article]:
        """키워드로 기사를 검색하여 반환한다."""
        pass

