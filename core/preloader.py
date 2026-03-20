# core/preloader.py
"""
앱 시작 시 무거운 라이브러리를 미리 로드하여 런타임 성능을 최적화합니다.
"""

import time
import importlib

# 1. 중량급 라이브러리 목록 (지연 로딩의 주범들)
HEAVY_LIBS = [
    "pandas",
    "numpy",
    "matplotlib",
    "matplotlib.pyplot",
    "matplotlib.font_manager",
    "scipy.stats",
    "scipy.linalg",
]


def warm_up(splash=None):
    """
    무거운 라이브러리를 미리 임포트하고 Matplotlib 등의 설정을 초기화합니다.
    """

    def _update_msg(msg):
        if splash:
            # 좌측 하단, Gold 색상 (#FFD700)으로 통일하여 가식성 확보
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QColor

            splash.showMessage(
                msg,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                QColor("white"),
            )
            from PyQt6.QtWidgets import QApplication

            QApplication.processEvents()
            # 메시지가 너무 빨리 지나가지 않도록 아주 미세한 지연 추가
            time.sleep(0.05)

    # 1. 라이브러리 사전 임포트
    for lib_name in HEAVY_LIBS:
        _update_msg(f"Loading {lib_name}...")
        try:
            importlib.import_module(lib_name)
        except Exception:
            pass

    # 2. Matplotlib 백엔드 및 폰트 워밍업
    _update_msg("Initializing Graphics Engine...")
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm

        # 백엔드 강제 초기화 및 캐시 생성
        plt.figure(figsize=(1, 1)).clear()
        plt.close("all")

        _update_msg("Loading Font Manager...")
        # 폰트 매니저 인스턴스화 (이게 가장 오래 걸리는 작업 중 하나)
        _ = fm.fontManager.ttflist

        _update_msg("Registering Assets Fonts...")
        from engine.plot_engine import _register_assets_fonts

        _register_assets_fonts()

    except Exception:
        pass

    # 3. 데이터 프로세서 및 엔진 사전 로딩
    _update_msg("Warming up Analysis Modules...")
    try:
        from model.data_processor import DataProcessor
        from engine.plot_engine import PlotEngine

        # 엔진 객체를 미리 생성하여 내부 정적 변수들 초기화
        _p = DataProcessor()
        _e = PlotEngine()

        # 추가적인 무거운 서브모듈 강제 로드
    except Exception:
        pass

    _update_msg("Preparing Main Interface...")

    _update_msg("Ready")
