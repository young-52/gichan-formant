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
    초기화된 객체(Startup Context)를 반환하여 메인 컨트롤러에서 재사용하게 합니다.
    """
    context = {
        "data_processor": None,
        "plot_engine": None,
        "live_preview_fig": None,
        "path_prefs": None,
    }

    def _update_msg(msg):
        if splash:
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QColor

            splash.showMessage(
                msg,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                QColor("white"),
            )
            from PyQt6.QtWidgets import QApplication

            QApplication.processEvents()
            time.sleep(0.02)  # 사용자 가독성을 위한 아주 미세한 지연

    # 1. 라이브러리 사전 임포트
    import sys

    for lib_name in HEAVY_LIBS:
        _update_msg(f"Loading {lib_name}...")
        try:
            if lib_name not in sys.modules:
                importlib.import_module(lib_name)
        except Exception:
            pass

    # 2. Matplotlib 백엔드 및 폰트 워밍업
    _update_msg("Initializing Graphics Engine...")
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        from matplotlib.figure import Figure

        # 2-1. 메인 컨트롤러에서 사용할 Figure 미리 생성 및 워밍업
        _update_msg("Warming up Graphics Canvas...")
        fig = Figure(figsize=(6.5, 6.5), dpi=150)
        fig.add_subplot(111).set_axis_off()  # 초기 빈 상태 설정
        context["live_preview_fig"] = fig

        # 2-2. 폰트 매니저 워밍업 (모음 분석 창 등에서 폰트 지연 방지)
        _update_msg("Scanning System Fonts...")
        fm.fontManager.get_default_weight()

        # 2-3. 기본 스타일 설정
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["axes.unicode_minus"] = False

    except Exception as e:
        print(f"Warning: Failed to warm up matplotlib: {e}")

    # 3. 기타 핵심 모듈 사전 로드
    _update_msg("Loading Core Engines...")
    try:
        # PlotEngine, PathPrefs 등
        from engine.plot_engine import PlotEngine
        # PathPrefs는 컨트롤러에서 직접 로드하므로 여기서 제외하여 타입 에러 방지

        # 컨트롤러에서 재사용할 수 있게 context에 담기
        context["plot_engine"] = PlotEngine()
        # context["path_prefs"] 제거 (AttributeError 방지)
    except Exception as e:
        print(f"Warning: Failed to pre-load core modules: {e}")

    _update_msg("System Ready")
    time.sleep(0.1)
    return context
