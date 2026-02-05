
from typing import Set
from domain.ports.storage_port import StorageRepository
from domain.model import Article

class MemoryStorageRepository(StorageRepository):
    """메모리 기반 저장소 구현체 (UI 앱용)"""
    
    def __init__(self):
        self.seen_ids: Set[int] = set()
        self.articles = []

    def load_today_ids(self) -> Set[int]:
        return self.seen_ids.copy()

    def save_article(self, article: Article) -> None:
        if article.id:
            self.seen_ids.add(article.id)
        self.articles.append(article)
