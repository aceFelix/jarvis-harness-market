"""WPS Office COM 后端管理 — 连接管理、进程检测、应用获取。

WPS Office 三个组件的 COM ProgID：
  - WPS 文字 (Writer):  Kwps.Application  (兼容 Word.Application)
  - WPS 表格 (Spreadsheet):  Ket.Application  (兼容 Excel.Application)
  - WPS 演示 (Presentation):  Kwpp.Application  (兼容 PowerPoint.Application)

当 WPS 未安装时，会回退到 Microsoft Office（如果安装了的话）。

@author aceFelix
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Any

# Windows-only COM 支持
_IS_WINDOWS = sys.platform == "win32"
if _IS_WINDOWS:
    try:
        import win32com.client
        import win32gui
        import win32process
        import pywintypes
        _HAS_PYWIN32 = True
    except ImportError:
        _HAS_PYWIN32 = False
else:
    _HAS_PYWIN32 = False


# ── ProgID 定义 ───────────────────────────────────────────────────────

# 优先 WPS，回退 MS Office
_PROGIDS = {
    "writer": ["Kwps.Application", "Word.Application"],
    "spreadsheet": ["Ket.Application", "Excel.Application"],
    "presentation": ["Kwpp.Application", "PowerPoint.Application"],
}


# ── 异常 ──────────────────────────────────────────────────────────────

class WPSBackendError(RuntimeError):
    """WPS COM 后端操作失败。"""


# ── 环境检测 ──────────────────────────────────────────────────────────

def is_windows() -> bool:
    """是否在 Windows 环境下。"""
    return _IS_WINDOWS


def has_pywin32() -> bool:
    """是否安装了 pywin32。"""
    return _HAS_PYWIN32


def check_environment() -> dict[str, Any]:
    """检测运行环境，返回环境状态字典。"""
    return {
        "status": "ok",
        "is_windows": _IS_WINDOWS,
        "has_pywin32": _HAS_PYWIN32,
        "can_run": _IS_WINDOWS and _HAS_PYWIN32,
    }


# ── COM 应用获取 ──────────────────────────────────────────────────────

def get_application(component: str, *, visible: bool = True) -> Any:
    """获取 WPS/Office COM 应用对象。

    优先尝试 WPS ProgID，失败后回退 MS Office ProgID。

    Args:
        component: 组件类型，"writer" / "spreadsheet" / "presentation"
        visible: 是否显示应用窗口

    Returns:
        COM Application 对象

    Raises:
        WPSBackendError: 环境不支持或无法连接
    """
    if not _IS_WINDOWS:
        raise WPSBackendError("WPS COM 自动化仅支持 Windows 系统")
    if not _HAS_PYWIN32:
        raise WPSBackendError(
            "缺少 pywin32 依赖，请运行: pip install pywin32"
        )

    progids = _PROGIDS.get(component)
    if not progids:
        raise WPSBackendError(f"未知组件类型: {component}")

    last_error = None
    for progid in progids:
        try:
            app = win32com.client.Dispatch(progid)
            try:
                app.Visible = visible
            except Exception:
                # 某些组件（如 Excel）的 Visible 可能在特定状态下不可设置
                pass
            return app
        except Exception as e:
            last_error = e
            continue

    raise WPSBackendError(
        f"无法启动 WPS/Office 组件 '{component}'。"
        f"请确认已安装 WPS Office 或 Microsoft Office。"
        f"最后错误: {last_error}"
    )


def get_writer_app(*, visible: bool = True) -> Any:
    """获取 WPS 文字应用。"""
    return get_application("writer", visible=visible)


def get_spreadsheet_app(*, visible: bool = True) -> Any:
    """获取 WPS 表格应用。"""
    return get_application("spreadsheet", visible=visible)


def get_presentation_app(*, visible: bool = True) -> Any:
    """获取 WPS 演示应用。"""
    return get_application("presentation", visible=visible)


# ── 进程检测 ──────────────────────────────────────────────────────────

def find_wps_processes() -> list[dict[str, str]]:
    """查找正在运行的 WPS 相关进程。

    Returns:
        进程信息列表，每项含 pid、name
    """
    if not _IS_WINDOWS:
        return []

    wps_process_names = {
        "wps.exe", "et.exe", "wpp.exe",
        "wpsoffice.exe", "ksolaunch.exe",
    }
    results: list[dict[str, str]] = []

    try:
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.strip().splitlines():
            parts = line.strip().strip('"').split('","')
            if len(parts) >= 2:
                name = parts[0].lower()
                if name in wps_process_names:
                    results.append({"pid": parts[1], "name": parts[0]})
    except Exception:
        pass

    return results


def is_wps_running() -> bool:
    """检测 WPS 进程是否正在运行。"""
    return len(find_wps_processes()) > 0


# ── 路径工具 ──────────────────────────────────────────────────────────

def resolve_path(path: str, workdir: str = "") -> str:
    """将路径解析为绝对路径。

    支持相对路径（相对于 workdir）、绝对路径、用户目录展开 (~)。

    Args:
        path: 输入路径
        workdir: 工作目录（用于解析相对路径）

    Returns:
        绝对路径字符串
    """
    if not path:
        return ""
    # 展开 ~
    path = os.path.expanduser(path)
    # 相对路径
    if not os.path.isabs(path) and workdir:
        path = os.path.join(workdir, path)
    return os.path.abspath(path)


def ensure_dir(path: str) -> str:
    """确保目录存在，返回绝对路径。"""
    path = resolve_path(path)
    os.makedirs(path, exist_ok=True)
    return path
