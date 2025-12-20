"""인포스탁 스크래퍼 디버그용 스크립트

실제 인포스탁에서 데이터를 가져와서 파싱 결과를 출력합니다.
"""

import asyncio
import sys
from pathlib import Path

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.news.scrapers.rss.infostock_scraper import InfostockScraper


async def main():
    scraper = InfostockScraper()
    keyword = "AI"
    
    print(f"🔍 인포스탁에서 '{keyword}' 검색 중...")
    print("=" * 80)
    
    try:
        articles = await scraper.fetch_reports(keyword)
        
        print(f"\n📊 총 {len(articles)}개 기사 발견\n")
        
        if not articles:
            print("❌ 기사가 없습니다.")
            return
        
        # 처음 5개 기사 출력
        for i, article in enumerate(articles[:5], 1):
            print(f"[{i}] 기사")
            print(f"  ID: {article.id}")
            print(f"  제목: {article.title}")
            print(f"  링크: {article.link}")
            print(f"  날짜: '{article.date}'")  # 따옴표로 감싸서 공백 확인
            print(f"  키워드: {article.keyword}")
            print(f"  출처: {article.source}")
            print()
        
        # 날짜 형식 분석
        print("\n📅 날짜 형식 분석")
        print("=" * 80)
        dates = [a.date for a in articles[:10]]
        for i, date in enumerate(dates, 1):
            print(f"{i}. '{date}' (길이: {len(date)})")
            # 날짜 형식 확인
            if '.' in date:
                print(f"   → '.'로 구분됨")
            if '-' in date:
                print(f"   → '-'로 구분됨")
            if ' ' in date:
                parts = date.split(' ')
                print(f"   → 공백으로 분리: {parts}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
