from abc import ABC, abstractmethod
from typing import Set
from src.domain.model import Article

class StorageRepository(ABC):
    @abstractmethod
    def load_today_ids(self) -> Set[int]:
        """오늘 저장된 기사 ID 목록을 불러온다."""
        pass

    @abstractmethod
    def save_article(self, article: Article) -> None:
        """기사 정보를 저장소에 저장한다."""
        pass
