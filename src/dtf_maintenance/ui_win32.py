"""Localisation lecture seule des boutons PrintExp (Win32). Aucun clic."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass

user32 = ctypes.WinDLL("user32", use_last_error=True)

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.EnumChildWindows.argtypes = [wintypes.HWND, WNDENUMPROC, wintypes.LPARAM]
user32.EnumChildWindows.restype = wintypes.BOOL
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.GetDlgCtrlID.argtypes = [wintypes.HWND]
user32.GetDlgCtrlID.restype = ctypes.c_int
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.IsWindowEnabled.argtypes = [wintypes.HWND]
user32.IsWindowEnabled.restype = wintypes.BOOL
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowRect.restype = wintypes.BOOL
user32.GetParent.argtypes = [wintypes.HWND]
user32.GetParent.restype = wintypes.HWND

# Resource IDs OBSERVÉS dump 2026-09-18 (PrintExp 5.8.1.1.29).
CLEAN_ID = 11030
CHECK_ID = 11029
WATCH = frozenset({"Clean", "Check", "OpenFiles", "Print", "Pause", "Cancel", "Flash"})


@dataclass(frozen=True)
class WinButton:
    hwnd: int
    ctrl_id: int
    text: str
    enabled: bool
    visible: bool
    left: int
    top: int
    right: int
    bottom: int


def is_minimized_rect(left: int, top: int) -> bool:
    """Windows place une fenêtre minimisée vers (-32000, -32000)."""
    return left <= -30000 or top <= -30000


def _text(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(hwnd, buf, 512)
    return buf.value


def _class(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def _pid_of(hwnd: int) -> int:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return int(pid.value)


def find_printexp_hwnd() -> int | None:
    found: list[int] = []

    def _cb(hwnd, _lparam):
        if _class(hwnd) == "#32770" and _text(hwnd) == "PrintExp":
            found.append(int(hwnd))
        return True

    cb = WNDENUMPROC(_cb)
    user32.EnumWindows(cb, 0)
    return found[0] if found else None


def list_watched_buttons(root: int) -> list[WinButton]:
    out: list[WinButton] = []

    def _cb(hwnd, _lparam):
        if _class(hwnd) != "Button":
            return True
        text = _text(hwnd)
        if text not in WATCH:
            return True
        rc = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rc))
        out.append(
            WinButton(
                hwnd=int(hwnd),
                ctrl_id=int(user32.GetDlgCtrlID(hwnd)),
                text=text,
                enabled=bool(user32.IsWindowEnabled(hwnd)),
                visible=bool(user32.IsWindowVisible(hwnd)),
                left=int(rc.left),
                top=int(rc.top),
                right=int(rc.right),
                bottom=int(rc.bottom),
            )
        )
        return True

    cb = WNDENUMPROC(_cb)
    user32.EnumChildWindows(root, cb, 0)
    return out


def describe_printexp_controls() -> list[str]:
    """Journal dry-run : où sont Clean/Check. N'envoie aucun BM_CLICK."""
    lines: list[str] = []
    root = find_printexp_hwnd()
    if root is None:
        return ["ui_win32: fenêtre PrintExp introuvable — aucun clic"]
    rc = wintypes.RECT()
    user32.GetWindowRect(root, ctypes.byref(rc))
    mini = is_minimized_rect(rc.left, rc.top)
    lines.append(
        f"ui_win32: PrintExp hwnd={root} rect={rc.left},{rc.top}-{rc.right},{rc.bottom} "
        f"minimized={mini} (lecture seule)"
    )
    buttons = list_watched_buttons(root)
    if not buttons:
        lines.append("ui_win32: aucun bouton Clean/Check vu — aucun clic")
        return lines
    for b in buttons:
        mark = ""
        if b.text == "Clean" and b.ctrl_id == CLEAN_ID:
            mark = " [id Clean CONFIRMÉ dump]"
        if b.text == "Check" and b.ctrl_id == CHECK_ID:
            mark = " [id Check CONFIRMÉ dump]"
        lines.append(
            f"ui_win32: {b.text} id={b.ctrl_id} hwnd={b.hwnd} en={b.enabled} vis={b.visible} "
            f"rect={b.left},{b.top}-{b.right},{b.bottom}{mark}"
        )
    clean = next((b for b in buttons if b.text == "Clean" and b.ctrl_id == CLEAN_ID), None)
    check = next((b for b in buttons if b.text == "Check" and b.ctrl_id == CHECK_ID), None)
    idleish = (
        any(b.text == "Print" and not b.enabled for b in buttons)
        and any(b.text == "Pause" and not b.enabled for b in buttons)
        and any(b.text == "Cancel" and not b.enabled for b in buttons)
        and clean is not None
        and clean.enabled
        and check is not None
        and check.enabled
    )
    lines.append(
        f"ui_win32: bandeau_idle_hypothese={idleish} "
        "(Print/Pause/Cancel disabled + Clean/Check enabled)"
    )
    lines.append("ui_win32: dry_run no BM_CLICK no menu")
    return lines
