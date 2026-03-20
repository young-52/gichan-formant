# utils/logger_setup.py
"""
Python 표준 logging 모듈을 사용한 백그라운드 전역 로깅 설정.
- 콘솔 출력 및 파일 출력(TimedRotatingFileHandler)을 담당합니다.
- GUI 로그창과는 별개로 동작하며, 상세한 디버그 정보를 날짜별로 기록합니다.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logging(log_dir="logs"):
    """
    애플리케이션 전역 로거를 초기화합니다.
    Returns: logging.Logger
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    logger = logging.getLogger("GichanFormant")

    # 중복 핸들러 방지
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    # 백그라운드용 상세 포맷: [시간] [레벨] [모듈] 메시지
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)8s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. 파일 핸들러 (TimedRotatingFileHandler: 일 단위, 7일 보관)
    file_handler = TimedRotatingFileHandler(
        log_file, when="D", interval=1, backupCount=7, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # 2. 콘솔 핸들러 (터미널 출력용)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    return logger
