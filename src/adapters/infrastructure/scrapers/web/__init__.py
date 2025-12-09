"""웹 스크래핑 기반 뉴스 스크래퍼 모음"""

from adapters.infrastructure.scrapers.web.hankyung_scraper import HankyungScraper
from adapters.infrastructure.scrapers.web.mt_scraper import MTScraper
from adapters.infrastructure.scrapers.web.newspim_scraper import NewspimScraper

__all__ = [
    'HankyungScraper',
    'MTScraper',
    'NewspimScraper',
]
