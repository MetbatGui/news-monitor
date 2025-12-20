import re
import httpx
from bs4 import BeautifulSoup
from typing import List
import logging

from infrastructure.news.dto import ArticleData
from domain.ports.news_port import NewsRepository

logger = logging.getLogger(__name__)

class InfostockScraper(NewsRepository):
    BASE_URL = "https://www.infostockdaily.co.kr"
    SEARCH_URL = "https://www.infostockdaily.co.kr/news/articleList.html"

    async def fetch_reports(self, keyword: str) -> List[ArticleData]:
        articles = []
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                "Referer": "https://www.infostockdaily.co.kr/news/articleList.html"
            }
            
            data = {
                "sc_area": "A",
                "view_type": "sm",
                "sc_word": keyword
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.SEARCH_URL, headers=headers, data=data, timeout=20)
                response.raise_for_status()
                # Fix encoding issue
                response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select(".list-block")
            
            for item in items:
                try:
                    # Title & Link
                    title_tag = item.select_one(".list-titles a")
                    if not title_tag:
                        continue
                        
                    title = title_tag.text.strip()
                    relative_link = title_tag['href']
                    link = self.BASE_URL + relative_link
                    
                    # ID Extraction
                    # Link format: /news/articleView.html?idxno=12345
                    article_id = 0
                    match = re.search(r'idxno=(\d+)', relative_link)
                    if match:
                        article_id = int(match.group(1))
                    else:
                        # Fallback if ID not found in URL (unlikely for this CMS)
                        continue

                    # Date
                    # Format: "국내주식 | 박상인 기자 | 2025-12-19 17:21"
                    # 또는 "정책·이슈 | 윤서연 기자 | 2025-12-19 13:55"
                    date_tag = item.select_one(".list-dated")
                    date_str = ""
                    if date_tag:
                        raw_date = date_tag.text.strip()
                        # "카테고리 | 기자명 | 날짜 시간" 형식에서 날짜 부분만 추출
                        if '|' in raw_date:
                            # 마지막 '|' 이후가 날짜
                            parts = raw_date.split('|')
                            if len(parts) >= 3:
                                date_str = parts[-1].strip()
                        else:
                            # '|'가 없으면 그대로 사용
                            date_str = raw_date
                    
                    articles.append(ArticleData(
                        id=article_id,
                        title=title,
                        link=link,
                        date=date_str,
                        keyword=keyword,
                        source=self.get_source_name()
                    ))
                    
                except Exception as e:
                    logger.debug(f"인포스탁 항목 파싱 오류: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"인포스탁 스크래핑 오류: {e}", exc_info=True)
            
        return articles

    def get_source_name(self) -> str:
        return "인포스탁"
