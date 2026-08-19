from __future__ import annotations

import ctypes
import ntpath
import sys
from ctypes import wintypes

from .base import Result

WM_APPCOMMAND = 0x0319
APPCOMMAND_MEDIA_NEXTTRACK = 11
APPCOMMAND_MEDIA_PREVIOUSTRACK = 12
APPCOMMAND_MEDIA_PLAY = 46
APPCOMMAND_MEDIA_PAUSE = 47
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def _find_window_for_process(
    process_name: str,
) -> int | None:
    if sys.platform != "win32":
        raise RuntimeError(
            "WM_APPCOMMAND transport is available only on Windows.",
        )

    user32 = ctypes.WinDLL(
        "user32",
        use_last_error=True,
    )
    kernel32 = ctypes.WinDLL(
        "kernel32",
        use_last_error=True,
    )

    callback_type = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HWND,
        wintypes.LPARAM,
    )

    user32.IsWindowVisible.argtypes = [
        wintypes.HWND,
    ]
    user32.IsWindowVisible.restype = wintypes.BOOL

    user32.GetWindowThreadProcessId.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(wintypes.DWORD),
    ]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD

    user32.EnumWindows.argtypes = [
        callback_type,
        wintypes.LPARAM,
    ]
    user32.EnumWindows.restype = wintypes.BOOL

    kernel32.OpenProcess.argtypes = [
        wintypes.DWORD,
        wintypes.BOOL,
        wintypes.DWORD,
    ]
    kernel32.OpenProcess.restype = wintypes.HANDLE

    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL

    kernel32.CloseHandle.argtypes = [
        wintypes.HANDLE,
    ]
    kernel32.CloseHandle.restype = wintypes.BOOL

    matches: list[int] = []

    def executable_name(
        pid: int,
    ) -> str:
        handle = kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION,
            False,
            pid,
        )
        if not handle:
            return ""

        try:
            size = wintypes.DWORD(32768)
            buffer = ctypes.create_unicode_buffer(
                size.value,
            )
            ok = kernel32.QueryFullProcessImageNameW(
                handle,
                0,
                buffer,
                ctypes.byref(size),
            )
            if not ok:
                return ""

            return ntpath.basename(
                buffer.value,
            )
        finally:
            kernel32.CloseHandle(
                handle,
            )

    @callback_type
    def callback(
        hwnd,
        _lparam,
    ):
        if not user32.IsWindowVisible(
            hwnd,
        ):
            return True

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(
            hwnd,
            ctypes.byref(pid),
        )

        if (
            executable_name(
                pid.value,
            ).casefold()
            == process_name.casefold()
        ):
            matches.append(
                int(hwnd),
            )
            return False

        return True

    user32.EnumWindows(
        callback,
        0,
    )

    return matches[0] if matches else None


def send_appcommand(
    process_name: str,
    command: int,
    success_message: str,
) -> Result:
    if not process_name:
        return Result(
            False,
            "Windows music.process_name or launch_command is required for WM_APPCOMMAND fallback.",
        )

    try:
        hwnd = _find_window_for_process(
            process_name,
        )
    except Exception as exc:
        return Result(
            False,
            f"Windows app-command error: {exc}",
        )

    if hwnd is None:
        return Result(
            False,
            f"Windows media window not found: {process_name}",
        )

    try:
        user32 = ctypes.WinDLL(
            "user32",
            use_last_error=True,
        )
        send_message = user32.SendMessageW
        send_message.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        send_message.restype = ctypes.c_ssize_t
        send_message(
            hwnd,
            WM_APPCOMMAND,
            hwnd,
            command << 16,
        )
    except Exception as exc:
        return Result(
            False,
            f"Windows app-command error: {exc}",
        )

    return Result(
        True,
        success_message,
    )
