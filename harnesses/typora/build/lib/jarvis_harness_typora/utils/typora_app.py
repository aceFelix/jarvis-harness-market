"""Typora 应用工具 — 定位可执行文件、启动打开、环境检测。

@author aceFelix
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _candidate_paths() -> list[Path]:
    """返回常见 Typora 安装路径（Windows）。"""
    env = os.environ
    paths = [
        Path(env.get("LOCALAPPDATA", "")) / "Programs" / "Typora" / "Typora.exe",
        Path(env.get("PROGRAMFILES", "")) / "Typora" / "Typora.exe",
        Path(env.get("PROGRAMFILES(X86)", "")) / "Typora" / "Typora.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "Typora" / "Typora.exe",
    ]
    return [p for p in paths if p]


def find_typora_exe() -> str | None:
    """定位 Typora 可执行文件（PATH 优先，其次常见安装路径）。"""
    exe = shutil.which("typora") or shutil.which("Typora")
    if exe:
        return exe
    for p in _candidate_paths():
        if p.is_file():
            return str(p)
    return None


def is_typora_running() -> bool:
    """检测 Typora 进程是否在运行（Windows 用 tasklist，macOS/Linux 用 pgrep）。"""
    try:
        if sys.platform == "win32":
            out = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Typora.exe"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=10,
            ).stdout
            return "typora.exe" in out.lower()
        out = subprocess.run(
            ["pgrep", "-x", "typora"], capture_output=True, text=True, timeout=10
        ).stdout
        return bool(out.strip())
    except Exception:
        return False


def open_in_typora(exe: str, path: str | None = None) -> None:
    """以分离进程方式启动 Typora 打开文档（不阻塞调用方）。"""
    cmd = [exe]
    if path:
        cmd.append(path)
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )


def get_environment() -> dict:
    """检测 Typora 环境状态（供 info 命令与容错提示）。"""
    exe = find_typora_exe()
    return {
        "is_windows": sys.platform == "win32",
        "typora_found": exe is not None,
        "typora_path": exe or "",
        "typora_running": is_typora_running() if exe else False,
    }
