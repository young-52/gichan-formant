from __future__ import annotations

from typing import List


class DrawManager:
    """그리기 도메인 상태 접근 전용 매니저."""

    def __init__(self, popup: object):
        self._popup = popup

    def get_draw_objects(self) -> List[object]:
        getter = getattr(self._popup, "_get_current_draw_objects", None)
        if getter is None:
            return []
        return getter() or []

    def set_draw_objects(self, objs: List[object]) -> None:
        setter = getattr(self._popup, "_set_current_draw_objects", None)
        if setter is not None:
            setter(objs)

    def redraw(self) -> None:
        redraw = getattr(self._popup, "_redraw_draw_layer", None)
        if redraw is not None:
            redraw()

    def notify_apply(self) -> None:
        if hasattr(self._popup, "on_apply"):
            self._popup.on_apply()
