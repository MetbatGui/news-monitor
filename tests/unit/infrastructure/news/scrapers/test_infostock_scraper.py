"""인포스탁 스크래퍼 파싱 로직 테스트

실제 HTML 파일을 사용하여 파싱 로직을 검증합니다.
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup
import re

from src.infrastructure.news.dto import ArticleData
from src.infrastructure.news.scrapers.rss.infostock_scraper import InfostockScraper


@pytest.fixture
def sample_html():
    """테스트용 실제 HTML 파일 로드"""
    # tests/unit/infrastructure/news/scrapers/ -> tests/data/
    html_path = Path(__file__).parents[4] / "data" / "infostock_ai_search.html"
    
    if not html_path.exists():
        pytest.skip(f"HTML 파일이 없습니다: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def scraper():
    """InfostockScraper 인스턴스"""
    return InfostockScraper()


class TestInfostockParsing:
    """인포스탁 HTML 파싱 테스트"""
    
    def test_parse_search_results(self, sample_html, scraper):
        """AI 검색 결과 파싱"""
        # Given
        soup = BeautifulSoup(sample_html, 'html.parser')
        items = soup.select(".list-block")
        keyword = "AI"
        
        # When
        articles = []
        for item in items:
            try:
                # Title & Link
                title_tag = item.select_one(".list-titles a")
                if not title_tag:
                    continue
                    
                title = title_tag.text.strip()
                relative_link = title_tag['href']
                link = scraper.BASE_URL + relative_link
                
                # ID Extraction
                article_id = 0
                match = re.search(r'idxno=(\d+)', relative_link)
                if match:
                    article_id = int(match.group(1))
                else:
                    continue
                
                # Date
                date_tag = item.select_one(".list-dated")
                date_str = ""
                if date_tag:
                    raw_date = date_tag.text.strip()
                    if raw_date:
                        date_str = raw_date.replace('.', '-', 2)
                
                articles.append(ArticleData(
                    id=article_id,
                    title=title,
                    link=link,
                    date=date_str,
                    keyword=keyword,
                    source=scraper.get_source_name()
                ))
                
            except Exception as e:
                continue
        
        # Then
        assert len(articles) > 0, "최소 1개 이상의 기사가 파싱되어야 합니다"
        
        # 첫 번째 기사 검증
        first_article = articles[0]
        assert first_article.id > 0, "기사 ID가 있어야 합니다"
        assert len(first_article.title) > 0, "제목이 있어야 합니다"
        assert first_article.link.startswith("https://"), "링크는 https로 시작해야 합니다"
        assert "idxno=" in first_article.link, "링크에 idxno 파라미터가 있어야 합니다"
        assert first_article.source == "인포스탁", "출처는 '인포스탁'이어야 합니다"
        assert first_article.keyword == "AI", "키워드는 'AI'여야 합니다"
    
    def test_selector_list_block_exists(self, sample_html):
        """.list-block 셀렉터가 존재하는지 확인"""
        # Given
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        # When
        items = soup.select(".list-block")
        
        # Then
        assert len(items) > 0, ".list-block 요소가 최소 1개 이상 있어야 합니다"
    
    def test_selector_title_link_exists(self, sample_html):
        """.list-titles a 셀렉터가 존재하는지 확인"""
        # Given
        soup = BeautifulSoup(sample_html, 'html.parser')
        items = soup.select(".list-block")
        
        # When
        title_links = [item.select_one(".list-titles a") for item in items]
        
        # Then
        valid_links = [link for link in title_links if link is not None]
        assert len(valid_links) > 0, ".list-titles a 요소가 최소 1개 이상 있어야 합니다"
    
    def test_id_extraction_pattern(self, sample_html):
        """idxno 파라미터 추출 패턴 테스트"""
        # Given
        soup = BeautifulSoup(sample_html, 'html.parser')
        items = soup.select(".list-block")
        
        # When
        extracted_ids = []
        for item in items:
            title_tag = item.select_one(".list-titles a")
            if title_tag and 'href' in title_tag.attrs:
                match = re.search(r'idxno=(\d+)', title_tag['href'])
                if match:
                    extracted_ids.append(int(match.group(1)))
        
        # Then
        assert len(extracted_ids) > 0, "최소 1개 이상의 ID가 추출되어야 합니다"
        assert all(id > 0 for id in extracted_ids), "모든 ID는 양수여야 합니다"
        assert len(set(extracted_ids)) == len(extracted_ids), "ID는 중복되지 않아야 합니다"
    
    def test_date_format_conversion(self, sample_html):
        """날짜 형식 변환 테스트 (YYYY.MM.DD -> YYYY-MM-DD)"""
        # Given
        soup = BeautifulSoup(sample_html, 'html.parser')
        items = soup.select(".list-block")
        
        # When
        dates = []
        for item in items:
            date_tag = item.select_one(".list-dated")
            if date_tag:
                raw_date = date_tag.text.strip()
                if raw_date:
                    # "2024.12.04 16:20" -> "2024-12-04 16:20"
                    converted = raw_date.replace('.', '-', 2)
                    dates.append(converted)
        
        # Then
        assert len(dates) > 0, "최소 1개 이상의 날짜가 추출되어야 합니다"
        
        # 날짜 형식 검증 (YYYY-MM-DD 포함)
        for date in dates[:3]:  # 처음 3개만 검증
            assert '-' in date, f"날짜에 '-'가 포함되어야 합니다: {date}"
