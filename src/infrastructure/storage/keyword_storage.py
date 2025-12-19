import json
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class KeywordStorage:
    def __init__(self, filepath: str = "config/keywords.json"):
        self.filepath = filepath
        self.base_dir = os.path.dirname(filepath)
        if self.base_dir:
            os.makedirs(self.base_dir, exist_ok=True)

    def load(self) -> Dict[str, List[str]]:
        if not os.path.exists(self.filepath):
            return {"keywords": [], "stock_names": []}
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"키워드 로드 오류: {e}")
            return {"keywords": [], "stock_names": []}

    def save(self, keywords: List[str], stock_names: List[str]) -> None:
        data = {
            "keywords": keywords,
            "stock_names": stock_names
        }
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"키워드 저장 오류: {e}")
