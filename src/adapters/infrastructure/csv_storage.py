import csv
import os
from datetime import datetime
from typing import Set

from src.domain.model import Article
from src.ports.storage_port import StorageRepository

class CsvStorage(StorageRepository):
    def __init__(self, base_dir: str = "logs"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_today_filename(self) -> str:
        today = datetime.now().strftime("%Y%m%d")
        return os.path.join(self.base_dir, f"report_{today}.csv")

    def load_today_ids(self) -> Set[int]:
        filename = self._get_today_filename()
        ids = set()
        
        if not os.path.exists(filename):
            return ids
            
        try:
            with open(filename, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].isdigit():
                        ids.add(int(row[0]))
        except Exception as e:
            print(f"Error loading CSV: {e}")
            
        return ids

    def save_article(self, article: Article) -> None:
        filename = self._get_today_filename()
        try:
            with open(filename, mode='a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                # Format: ID, Title, Link, Date, SavedAt
                writer.writerow([
                    article.id,
                    article.title,
                    article.link,
                    article.date,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
        except Exception as e:
            print(f"Error saving to CSV: {e}")
