"""웹 스크래핑 기반 뉴스 스크래퍼 모음"""

from adapters.infrastructure.scrapers.web.fn_scraper import FnScraper
from adapters.infrastructure.scrapers.web.mt_scraper import MTScraper

__all__ = [
    'FnScraper',
    'MTScraper',
]
