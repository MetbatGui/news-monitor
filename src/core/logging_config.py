"""
로깅 설정 모듈

colorama를 사용한 컬러 로깅 지원
파일 및 콘솔 출력 설정
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from colorama import Fore, Back, Style, init

# colorama 초기화 (Windows 호환성)
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """컬러 출력을 지원하는 로깅 포맷터"""
    
    # 로그 레벨별 색상 정의
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    # 특수 문자 색상
    SYMBOLS = {
        'DEBUG': Fore.CYAN + '🔍',
        'INFO': Fore.GREEN + '✓',
        'WARNING': Fore.YELLOW + '⚠',
        'ERROR': Fore.RED + '✗',
        'CRITICAL': Fore.RED + '💥',
    }
    
    def __init__(self, fmt=None, datefmt=None, use_colors=True):
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors
    
    def format(self, record):
        if self.use_colors:
            # 로그 레벨에 색상 추가
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.SYMBOLS.get(levelname, '')} {self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
                record.name = f"{Fore.BLUE}{record.name}{Style.RESET_ALL}"
        
        return super().format(record)


def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """
    로깅 시스템 설정
    
    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 로그 파일 저장 디렉토리
    """
    # 로그 디렉토리 생성
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 로그 레벨 설정
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()
    
    # 1. 콘솔 핸들러 (컬러)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        use_colors=True
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 2. 파일 핸들러 (일반, 모든 로그)
    file_handler = RotatingFileHandler(
        filename=log_path / 'news_monitor.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # 파일에는 모든 레벨 기록
    file_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 3. 에러 파일 핸들러 (ERROR 이상만)
    error_handler = RotatingFileHandler(
        filename=log_path / 'errors.log',
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # 초기화 메시지
    logger = logging.getLogger(__name__)
    logger.info(f"로깅 시스템 초기화 완료 (레벨: {log_level})")
    logger.info(f"로그 파일: {log_path.absolute()}")


def get_logger(name: str) -> logging.Logger:
    """
    모듈별 로거 가져오기
    
    Args:
        name: 로거 이름 (보통 __name__ 사용)
    
    Returns:
        Logger 인스턴스
    """
    return logging.getLogger(name)
