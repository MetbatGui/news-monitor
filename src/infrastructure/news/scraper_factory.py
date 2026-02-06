from typing import List
from domain.ports.news_port import NewsScraper

from infrastructure.news.scrapers.rss.newspim_rss_scraper import NewspimRssScraper
from infrastructure.news.scrapers.rss.edaily_rss_scraper import EdailyRssScraper
from infrastructure.news.scrapers.rss.hankyung_rss_scraper import HankyungRssScraper
from infrastructure.news.scrapers.rss.mk_rss_scraper import MKRssScraper
from infrastructure.news.scrapers.web.mt_scraper import MTScraper
from infrastructure.news.scrapers.rss.yonhap_rss_scraper import YonhapRssScraper
from infrastructure.news.scrapers.rss.asiae_rss_scraper import AsiaeRssScraper
from infrastructure.news.scrapers.rss.etoday_rss_scraper import EtodayRssScraper
from infrastructure.news.scrapers.rss.herald_rss_scraper import HeraldRssScraper
from infrastructure.news.scrapers.rss.seoul_rss_scraper import SeoulRssScraper
from infrastructure.news.scrapers.web.fn_scraper import FnScraper
from infrastructure.news.scrapers.rss.infostock_scraper import InfostockScraper
from infrastructure.news.scrapers.rss.dart_rss_scraper import DartRssScraper

class ScraperFactory:
    """모든 뉴스 스크래퍼 인스턴스를 생성하고 관리하는 팩토리 클래스"""

    @staticmethod
    def create_all_scrapers() -> List[NewsScraper]:
        """등록된 모든 스크래퍼 인스턴스를 생성하여 반환"""
        return [
            NewspimRssScraper(),
            EdailyRssScraper(),
            HankyungRssScraper(),
            MKRssScraper(),
            MTScraper(),
            YonhapRssScraper(),
            AsiaeRssScraper(),
            EtodayRssScraper(),
            HeraldRssScraper(),
            SeoulRssScraper(),
            FnScraper(),
            InfostockScraper(),
            DartRssScraper()
        ]
