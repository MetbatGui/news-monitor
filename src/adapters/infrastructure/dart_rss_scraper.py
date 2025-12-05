import requests
import xml.etree.ElementTree as ET
from typing import List
from datetime import datetime

from domain.model import Article
from ports.news_port import NewsRepository


class DartRssScraper(NewsRepository):
    """DART 전자공시 RSS 피드에서 공시 정보를 가져오는 스크래퍼"""
    
    def __init__(self, rss_url: str = "https://dart.fss.or.kr/api/todayRSS.xml"):
        self.rss_url = rss_url
    
    def fetch_reports(self, keyword: str = "") -> List[Article]:
        """RSS 피드에서 공시 정보를 가져옵니다.
        
        Args:
            keyword: 필터링할 키워드 (제목 또는 회사명에서 검색)
                    빈 문자열이면 모든 항목 반환
        
        Returns:
            Article 리스트
        """
        articles = []
        
        try:
            response = requests.get(self.rss_url, timeout=20)
            response.raise_for_status()
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            # RSS 2.0 네임스페이스
            ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
            
            # 각 item 처리
            for item in root.findall('.//item'):
                try:
                    # 필드 추출
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    category_elem = item.find('category')
                    pub_date_elem = item.find('pubDate')
                    creator_elem = item.find('dc:creator', ns)
                    guid_elem = item.find('guid')
                    
                    title = title_elem.text if title_elem is not None and title_elem.text else ""
                    link = link_elem.text if link_elem is not None and link_elem.text else ""
                    category = category_elem.text if category_elem is not None and category_elem.text else ""
                    pub_date = pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else ""
                    creator = creator_elem.text if creator_elem is not None and creator_elem.text else ""
                    guid = guid_elem.text if guid_elem is not None and guid_elem.text else ""
                    
                    # 키워드 필터링 (keyword가 지정된 경우)
                    # 제목, 회사명, 카테고리 중 하나라도 키워드 포함하면 통과
                    if keyword:
                        keyword_lower = keyword.lower()
                        title_lower = title.lower()
                        creator_lower = creator.lower()
                        category_lower = category.lower()
                        
                        if not (keyword_lower in title_lower or 
                                keyword_lower in creator_lower or 
                                keyword_lower in category_lower):
                            continue
                    
                    # guid에서 rcpNo 추출 (ID로 사용)
                    article_id = self._extract_rcp_no(guid)
                    
                    # pubDate 포맷 변환: "Fri, 05 Dec 2025 04:28:00 GMT" -> "2025-12-05 04:28"
                    date_str = self._convert_date_format(pub_date)
                    
                    # Article 생성 (title에 category와 creator 포함)
                    full_title = f"({category}){creator} - {title}"
                    
                    articles.append(Article(
                        id=article_id,
                        title=full_title,
                        link=link,
                        date=date_str,
                        keyword=keyword if keyword else category
                    ))
                    
                except Exception as e:
                    print(f"Error parsing RSS item: {e}")
                    continue
                    
        except Exception as e:
            print(f"RSS fetching error: {e}")
            
        return articles
    
    def _extract_rcp_no(self, guid: str) -> int:
        """GUID에서 rcpNo 추출
        
        Args:
            guid: GUID 문자열 (예: "https://dart.fss.or.kr/api/link.jsp?rcpNo=20251205000173")
            
        Returns:
            rcpNo (정수)
        """
        import re
        match = re.search(r'rcpNo=(\d+)', guid)
        return int(match.group(1)) if match else 0
    
    def _convert_date_format(self, pub_date: str) -> str:
        """RFC-822 날짜를 YYYY-MM-DD HH:MM 포맷으로 변환
        
        Args:
            pub_date: RFC-822 형식 날짜 (예: "Fri, 05 Dec 2025 04:28:00 GMT")
            
        Returns:
            변환된 날짜 문자열 (예: "2025-12-05 04:28")
        """
        try:
            # RFC-822 형식 파싱
            dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            # KST 시간대로 변환 (+9시간)
            from datetime import timedelta
            dt_kst = dt + timedelta(hours=9)
            return dt_kst.strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            print(f"Date conversion error for '{pub_date}': {e}")
            return pub_date  # 파싱 실패시 원본 반환
