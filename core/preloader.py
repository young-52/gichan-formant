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
    for lib_name in HEAVY_LIBS:
        _update_msg(f"Loading {lib_name}...")
        try:
            importlib.get_module(lib_name) if lib_name in importlib.sys.modules else importlib.import_module(lib_name)
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

        # 백엔드 강제 초기화 및 캐시 생성
        plt.figure(figsize=(1, 1)).clear()
        plt.close("all")

        _update_msg("Loading Font Manager...")
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

        context["data_processor"] = DataProcessor()
        context["plot_engine"] = PlotEngine()
    except Exception:
        pass

    # 4. 사용자 설정(Path Prefs) 선행 로드
    _update_msg("Loading User Preferences...")
    try:
        from PyQt6.QtCore import QStandardPaths
        from utils import path_prefs
        _prefs_base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if _prefs_base:
            context["path_prefs"] = path_prefs.load_path_prefs(_prefs_base)
    except Exception:
        pass

    _update_msg("Ready")
    return context
