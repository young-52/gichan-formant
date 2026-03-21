# main.py — 진입점

import sys
import platform
import os
import sentry_sdk
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QFont, QColor
from PySide6.QtCore import Qt

import config

# Sentry 초기화 (가장 먼저 실행하여 모든 오류를 포착)
sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    send_default_pii=config.SENTRY_SEND_PII,
)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. 스플래시 스크린 즉시 설정 (가장 최우선 순위로 실행하여 시각적 반응성 극대화)
    import os
    from PySide6.QtGui import QPixmap, QFont, QColor
    from PySide6.QtCore import Qt

    SPLASH_WIDTH = 450
    splash_path = os.path.join(config.ASSETS_DIR, "GichanFormant_SplashScreen.jpg")
    splash_pix = QPixmap(splash_path)

    # 스플래시 이미지 로드 실패 시 폴백 처리
    if splash_pix.isNull():
        splash_pix = QPixmap(SPLASH_WIDTH, int(SPLASH_WIDTH * 0.6))
        splash_pix.fill(QColor("#1976D2"))
        from PySide6.QtGui import QPainter

        painter = QPainter(splash_pix)
        painter.setPen(QColor("white"))
        font = QFont("Malgun Gothic", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            splash_pix.rect(), Qt.AlignmentFlag.AlignCenter, "GichanFormant\nLoading..."
        )
        painter.end()

    # DPI 대응 리사이징 (한 번만 수행)
    dpr = app.primaryScreen().devicePixelRatio()
    scaled_pix = splash_pix.scaledToWidth(
        int(SPLASH_WIDTH * dpr), Qt.TransformationMode.SmoothTransformation
    )
    scaled_pix.setDevicePixelRatio(dpr)

    class VersionSplashScreen(QSplashScreen):
        def __init__(self, pixmap, version):
            super().__init__(
                pixmap,
                Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint,
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setStyleSheet("background: transparent; border: none;")
            self.version = version
            self.version_font = QFont("Malgun Gothic", 9)

        def drawContents(self, painter):
            super().drawContents(painter)
            painter.setRenderHint(painter.RenderHint.Antialiasing)
            painter.setPen(QColor("white"))
            painter.setFont(self.version_font)
            painter.drawText(
                self.rect().adjusted(0, 10, -15, 0),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
                self.version,
            )

    splash = VersionSplashScreen(scaled_pix, f"Version {config.APP_VERSION}")
    splash.show()
    app.processEvents()

    # 2. 스플래시가 뜬 '이후' 로깅 및 기타 설정 초기화
    from utils import logger_setup
    import app_logger

    logger_setup.setup_logging()

    if platform.system() == "Windows":
        import ctypes

        try:
            myappid = "gichan.formant.app"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    app.setApplicationName("GichanFormant")
    app.setApplicationVersion(config.APP_VERSION)
    app.setOrganizationName(config.AUTHOR)
    app.setOrganizationDomain("com.gichan.formant")

    # 스플래시가 뜬 직후 무거운 유틸리티 및 프리로더 로드
    from utils import icon_utils
    from core import preloader

    # 전역 앱 레벨에서 아이콘 적용
    try:
        app.setWindowIcon(icon_utils.get_app_icon())
    except Exception:
        pass

    app_logger.set_min_level_from_env()

    # 3. 라이브러리 및 엔진 사전 로딩 (스플래시 업데이트 포함)
    startup_context = preloader.warm_up(splash)

    # UI 로딩 상태를 스플래시에 중계하기 위한 콜백 함수
    def status_callback(msg):
        if splash:
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QColor

            splash.showMessage(
                msg,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                QColor("white"),
            )
            app.processEvents()

    # 4. 메인 컨트롤러 생성 및 실행 (사전 초기화된 객체 및 콜백 전달)
    from core.controller import MainController

    controller = MainController(
        startup_context=startup_context, status_callback=status_callback
    )

    # 메인 윈도우가 준비되면 창을 띄우고 스플래시 종료
    if hasattr(controller, "ui") and controller.ui:
        controller.ui.show()
        splash.finish(controller.ui)
    else:
        splash.close()

    sys.exit(app.exec())
