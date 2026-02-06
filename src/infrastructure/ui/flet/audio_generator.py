import threading
import logging
from typing import List
from infrastructure.alerts.tts_service import TTSService

logger = logging.getLogger(__name__)

class BackgroundAudioGenerator:
    """TTS 오디오 파일을 백그라운드에서 생성하는 클래스"""
    
    def __init__(self, tts_service: TTSService):
        self.tts = tts_service

    def pre_generate_initial_audio(self, keywords: List[str]):
        """초기 오디오 파일 생성 (뉴스 소스 및 초기 키워드)"""
        threading.Thread(target=self._generate_initial_task, args=(keywords,), daemon=True).start()

    def generate_for_new_keywords(self, keywords: List[str]):
        """새로운 키워드에 대한 오디오 생성"""
        threading.Thread(target=self._generate_task, args=(keywords,), daemon=True).start()
        logger.info(f"키워드 변경 감지, {len(keywords)}개 항목 TTS 오디오 백그라운드 생성 중...")

    def _generate_initial_task(self, keywords: List[str]):
        logger.info("키워드 오디오 사전 생성 중...")
        sources = [
            "뉴스핌", "인포스탁", "DART", "이데일리", "한국경제", "매일경제",
            "머니투데이", "연합뉴스", "아시아경제", "이투데이", "헤럴드경제",
            "서울경제", "파이낸셜뉴스"
        ]
        
        for source in sources:
            self._safe_generate(source)
        
        for k in keywords:
            self._safe_generate(k)

    def _generate_task(self, keywords: List[str]):
        for k in keywords:
            self._safe_generate(k)

    def _safe_generate(self, text: str):
        try:
            self.tts.generate_audio(text)
        except Exception as e:
            logger.debug(f"'{text}' 오디오 생성 오류: {e}")
