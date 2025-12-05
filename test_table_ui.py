import flet as ft
import sys
sys.path.insert(0, 'src')

from infra.flet.components.article_table import ArticleTable
from domain.model import Article
from datetime import datetime

def main(page: ft.Page):
    page.title = "테이블 UI 테스트"
    page.padding = 20
    
    # 테스트 아티클 생성 (20개)
    test_articles = []
    base_time = datetime.now()
    
    sources = [
        ("뉴스핌", "https://www.newspim.com/news/view/202512050000"),
        ("인포스탁", "https://www.infostockdaily.co.kr/news/articleView.html?idxno=2123"),
        ("DART", "https://dart.fss.or.kr/api/link.jsp?rcpNo=202512050001"),
    ]
    
    titles = [
        "[리포트 브리핑] 삼성전자, 'AI 반도체 시장 공략' - 하나증권",
        "현대차, 전기차 신모델 출시 예정… 시장 기대감 상승",
        "(유가)카카오 - 주요사항보고서(자기주식취득결정)",
        "[리포트 브리핑] NAVER, '클라우드 사업 확대' - 미래에셋증권",
        "(코스닥)셀트리온헬스케어 - 단일판매·공급계약체결",
        "SK하이닉스, HBM3E 양산 본격화… 글로벌 시장 선점",
        "(유가)LG에너지솔루션 - 타법인 주식 및 출자증권 취득결정",
        "[리포트 브리핑] 포스코홀딩스, '2차전지 소재 성장' - KB증권",
        "기아, 전기차 EV9 수출 확대… 북미 시장 공략 강화",
        "(코스닥)에코프로비엠 - 최대주주등소유주식변동신고서",
        "[글로벌 마켓 리포트] 미국 기준금리 동결 전망",
        "(유가)삼성SDI - 주요사항보고서(주식등의대량보유상황보고)",
        "두산에너빌리티, SMR 수주 확대… 원전 사업 모멘텀",
        "(코스닥)알테오젠 - 최대주주변경을수반하는주식담보제공계약체결",
        "[리포트 브리핑] 한화솔루션, '태양광 사업 재편' - 신한투자",
        "(유가)현대모비스 - 타법인 주식 및 출자증권 취득결정",
        "LG Display, OLED TV 패널 수주 증가… 실적 턴어라운드 기대",
        "(코스닥)메디톡스 - 영업(잠정)실적(공정공시)",
        "[리포트 브리핑] HD현대일렉트릭, '변압기 수주 급증' - 대신증권",
        "(유가)삼성생명 - 주요사항보고서(자기주식취득결정)",
    ]
    
    keywords = ["삼성전자", "전기차", "유가", "클라우드", "코스닥", 
                "AI반도체", "2차전지", "리포트", "수출", "공시",
                "금리", "대량보유", "원전", "바이오", "태양광",
                "OLED", "실적", "변압기", "자기주식", "증권"]
    
    for i in range(20):
        source_type = i % 3
        source_name, base_link = sources[source_type]
        
        minutes_ago = i * 15
        article_time = base_time - timedelta(minutes=minutes_ago)
        
        test_articles.append(Article(
            id=i + 1,
            title=titles[i],
            link=f"{base_link}{str(i+1).zfill(2)}",
            date=article_time.strftime("%Y-%m-%d %H:%M"),
            keyword=keywords[i]
        ))
    
    
    # 테이블 생성
    article_table = ArticleTable()
    
    # 최근 기사 (첫 번째) 하이라이트
    highlighted_links = {test_articles[0].link}
    article_table.set_articles(test_articles, highlighted_links)
    
    # 페이지에 추가
    page.add(
        ft.Text("기사 테이블 UI 테스트", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Text("✨ 첫 번째 기사는 하이라이트(노란색) 처리됩니다", size=12, color=ft.Colors.GREY),
        ft.Text("👆 기사를 클릭하면 해당 링크가 열립니다", size=12, color=ft.Colors.GREY),
        ft.Divider(),
        article_table
    )

if __name__ == "__main__":
    ft.app(target=main)
