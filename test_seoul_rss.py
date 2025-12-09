"""서울경제 RSS 파싱 테스트"""
import asyncio
import sys
sys.path.insert(0, 'src')

from adapters.infrastructure.scrapers.rss.seoul_rss_scraper import SeoulRssScraper

async def test_seoul_rss():
    scraper = SeoulRssScraper()
    
    print("서울경제 RSS 피드 가져오기...")
    articles = await scraper.fetch_reports("태안")
    
    print(f"\n✅ 성공! {len(articles)}개 기사 발견")
    
    if articles:
        print("\n첫 번째 기사:")
        print(f"  제목: {articles[0].title}")
        print(f"  링크: {articles[0].link}")
        print(f"  날짜: {articles[0].date}")
        print(f"  출처: {articles[0].source}")

if __name__ == "__main__":
    asyncio.run(test_seoul_rss())
