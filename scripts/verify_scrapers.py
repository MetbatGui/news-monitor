
import sys
import os
from pathlib import Path
import logging

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / "src"))

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
from infrastructure.news.scrapers.rss.newspim_rss_scraper import NewspimRssScraper

# 인코딩 설정 (Windows 대응)
sys.stdout.reconfigure(encoding='utf-8')

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ScraperVerifier")

def verify_scrapers():
    scrapers = [
        ("Newspim", NewspimRssScraper()),
        ("Edaily", EdailyRssScraper()),
        ("Hankyung", HankyungRssScraper()),
        ("MK", MKRssScraper()),
        ("MoneyToday", MTScraper()),
        ("Yonhap", YonhapRssScraper()),
        ("Asiae", AsiaeRssScraper()),
        ("Etoday", EtodayRssScraper()),
        ("Herald", HeraldRssScraper()),
        ("Seoul", SeoulRssScraper()),
        ("FnGuide", FnScraper()),
        ("Infostock", InfostockScraper()),
        ("Dart", DartRssScraper())
    ]

    print(f"\n{'='*50}")
    print(f"뉴스 스크래퍼 동작 검증 시작 (총 {len(scrapers)}개)")
    print(f"{'='*50}\n")

    success_count = 0
    failed_scrapers = []
    
    keyword = "삼성전자" # 테스트 키워드

    for name, scraper in scrapers:
        print(f"[{name}] 검증 중...", end=" ", flush=True)
        try:
            # 동기 호출로 변경되었으므로 await 없음
            articles = scraper.fetch_reports(keyword)
            
            if articles:
                print(f"[OK] 성공 (기사 {len(articles)}개)")
                # 샘플 기사 출력
                print(f"   L 최신 기사: {articles[0].title} ({articles[0].date})")
                success_count += 1
            else:
                print(f"[WARN] 데이터 없음 (성공했으나 결과 0건)")
                # 일부 RSS는 키워드 검색을 지원하지 않거나 결과가 없을 수 있음
                success_count += 1 

        except Exception as e:
            print(f"[FAIL] 실패")
            print(f"   L 오류: {e}")
            failed_scrapers.append((name, str(e)))

    print(f"\n{'='*50}")
    print(f"검증 완료: 성공 {success_count}/{len(scrapers)}")
    if failed_scrapers:
        print(f"실패한 스크래퍼 목록:")
        for name, error in failed_scrapers:
            print(f"- {name}: {error}")
    print(f"{'='*50}")

if __name__ == "__main__":
    verify_scrapers()
