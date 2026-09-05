"""Keep the cheat overlay above fullscreen games."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QWidget

# Fullscreen games sit above normal "always on top" windows.
# Screensaver level + fullscreen-auxiliary lets the overlay join a game Space.
_MAC_SCREENSAVER_LEVEL = 1000
_MAC_JOIN_ALL_SPACES = 1 << 0
_MAC_MOVE_TO_ACTIVE_SPACE = 1 << 1
_MAC_STATIONARY = 1 << 4
_MAC_IGNORES_CYCLE = 1 << 6
_MAC_FULLSCREEN_AUXILIARY = 1 << 8


def pin_overlay(widget: QWidget, bring_front: bool = True) -> None:
    try:
        if sys.platform == "darwin":
            _pin_macos(widget, bring_front=bring_front)
        elif sys.platform == "win32":
            _pin_windows(widget)
        elif bring_front:
            widget.raise_()
    except Exception:
        if bring_front:
            widget.raise_()


def _pin_macos(widget: QWidget, bring_front: bool) -> None:
    try:
        import objc
        from AppKit import NSPanel
    except ImportError:
        widget.raise_()
        return

    widget.winId()
    try:
        view = objc.objc_object(c_void_p=int(widget.winId()))
    except Exception:
        widget.raise_()
        return
    if view is None:
        return

    window = view.window() if hasattr(view, "window") else None
    if window is None:
        return

    behavior = (
        _MAC_JOIN_ALL_SPACES
        | _MAC_STATIONARY
        | _MAC_IGNORES_CYCLE
        | _MAC_FULLSCREEN_AUXILIARY
    )
    window.setLevel_(_MAC_SCREENSAVER_LEVEL)
    window.setHidesOnDeactivate_(False)
    window.setCollectionBehavior_(behavior)
    window.setCanHide_(False)
    if isinstance(window, NSPanel):
        window.setFloatingPanel_(True)
        window.setBecomesKeyOnlyIfNeeded_(True)
    if bring_front:
        window.orderFrontRegardless()


def _pin_windows(widget: QWidget) -> None:
    try:
        import ctypes
    except ImportError:
        widget.raise_()
        return
    hwnd = int(widget.winId())
    hwnd_topmost = -1
    swp_nomove = 0x0002
    swp_nosize = 0x0001
    swp_showwindow = 0x0040
    ctypes.windll.user32.SetWindowPos(
        hwnd,
        hwnd_topmost,
        0,
        0,
        0,
        0,
        swp_nomove | swp_nosize | swp_showwindow,
    )
