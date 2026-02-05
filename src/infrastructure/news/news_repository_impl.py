
import logging
import concurrent.futures
from typing import List
from domain.ports.news_port import NewsRepository
from infrastructure.news.dto import ArticleData

logger = logging.getLogger(__name__)

class NewsRepositoryImpl(NewsRepository):
    """여러 스크래퍼를 관리하고 병렬로 데이터를 수집하는 Repository 구현체"""
    
    def __init__(self, scrapers: List):
        self.scrapers = scrapers
        
    def fetch_reports(self, keyword: str) -> List[ArticleData]:
        """모든 스크래퍼를 병렬로 실행하여 키워드 검색 결과를 반환"""
        all_articles = []
        
        # 스레드 풀을 사용하여 모든 스크래퍼 병렬 실행
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 각 스크래퍼의 fetch_reports 호출
            future_to_scraper = {
                executor.submit(scraper.fetch_reports, keyword): scraper 
                for scraper in self.scrapers
            }
            
            for future in concurrent.futures.as_completed(future_to_scraper):
                scraper = future_to_scraper[future]
                try:
                    articles = future.result()
                    if articles:
                        all_articles.extend(articles)
                except Exception as e:
                    logger.error(f"{scraper.__class__.__name__} 스크래핑 오류: {e}")
                    
        return all_articles
