import asyncio
import re
from datetime import datetime
import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from adapters.infrastructure.scrapers.web.mt_scraper import MTScraper
from adapters.infrastructure.scrapers.web.fn_scraper import FnScraper
from adapters.infrastructure.scrapers.rss.newspim_rss_scraper import NewspimRssScraper
from adapters.infrastructure.scrapers.rss.edaily_rss_scraper import EdailyRssScraper
from adapters.infrastructure.scrapers.rss.hankyung_rss_scraper import HankyungRssScraper
from adapters.infrastructure.scrapers.rss.mk_rss_scraper import MKRssScraper
from adapters.infrastructure.scrapers.rss.yonhap_rss_scraper import YonhapRssScraper
from adapters.infrastructure.scrapers.rss.asiae_rss_scraper import AsiaeRssScraper
from adapters.infrastructure.scrapers.rss.etoday_rss_scraper import EtodayRssScraper
from adapters.infrastructure.scrapers.rss.herald_rss_scraper import HeraldRssScraper
from adapters.infrastructure.scrapers.rss.seoul_rss_scraper import SeoulRssScraper
from adapters.infrastructure.scrapers.rss.infostock_scraper import InfostockScraper
from adapters.infrastructure.scrapers.rss.dart_rss_scraper import DartRssScraper
from config import DartConfig

async def main():
    scrapers = [
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
        DartRssScraper(DartConfig.RSS_URL)
    ]

    print(f"Testing {len(scrapers)} scrapers for date format compliance (YYYY-MM-DD...)...")
    
    # Use a generic keyword likely to return results
    keyword = "삼성전자"
    
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}')

    for scraper in scrapers:
        source_name = scraper.get_source_name()
        print(f"\nScanning {source_name}...")
        try:
            articles = await scraper.fetch_reports(keyword)
            if not articles:
                print(f"  [WARN] No articles found for '{keyword}'. Skipping date check.")
                continue
                
            example_date = articles[0].date
            print(f"  Sample date: '{example_date}'")
            
            if date_pattern.match(example_date):
                print(f"  [PASS] Date format looks correct.")
            else:
                print(f"  [FAIL] Invalid date format! Expected YYYY-MM-DD..., got '{example_date}'")
                
        except Exception as e:
            print(f"  [ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(main())
