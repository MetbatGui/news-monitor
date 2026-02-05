
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> None:
    """
    로깅 시스템을 초기화합니다.
    
    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 로그 파일을 저장할 디렉토리 경로
    """
    # 로그 디렉토리 생성 (프로젝트 루트 기준)
    # src/config/logging_config.py 위치에서 프로젝트 루트(../../) 계산
    project_root = Path(__file__).resolve().parent.parent.parent
    log_path = project_root / log_dir
    log_path.mkdir(exist_ok=True, parents=True)
    
    # 로그 파일명 (날짜별)
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"app_{current_date}.log"
    
    # 기본 포맷
    log_format = '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, date_format)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 기존 핸들러 제거 (중복 방지)
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # 1. 파일 핸들러 (Rotating)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 2. 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging initialized. Level: {log_level}, File: {log_file}")
