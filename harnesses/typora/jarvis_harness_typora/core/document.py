"""jarvis-harness-typora — Typora Markdown 编辑器文件操作核心逻辑。

纯 Python 实现，直接读写 .md 文件，不依赖 Typora 打开状态（Typora 自动保存）。

@author aceFelix
"""

from __future__ import annotations

import os
from pathlib import Path

_MD_SUFFIXES = (".md", ".markdown")
_READ_CAP = 100_000  # read 返回内容的字符上限


def resolve_path(path: str, workdir: str = "") -> str:
    """将路径解析为绝对路径。

    支持相对路径（相对于 workdir）、绝对路径、用户目录展开 (~)。
    """
    if not path:
        return ""
    path = os.path.expanduser(path)
    if not os.path.isabs(path) and workdir:
        path = os.path.join(workdir, path)
    return os.path.abspath(path)


def ensure_md_ext(path: str) -> str:
    """确保路径以 .md/.markdown 结尾（无后缀时补 .md）。"""
    if path and not Path(path).suffix:
        return path + ".md"
    return path


def read_document(path: str) -> dict:
    """读取文档内容。"""
    if not os.path.isfile(path):
        return {"status": "error", "message": f"文件不存在: {path}"}
    text = Path(path).read_text(encoding="utf-8")
    truncated = len(text) > _READ_CAP
    if truncated:
        text = text[:_READ_CAP]
    return {
        "status": "ok",
        "path": path,
        "content": text,
        "truncated": truncated,
        "char_count": len(text),
    }


def write_document(path: str, content: str) -> dict:
    """写入/覆盖文档内容。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")
    return {"status": "ok", "message": f"已写入: {path}"}


def append_document(path: str, content: str) -> dict:
    """追加内容到文档末尾。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            f.write("\n")
        f.write(content)
    return {"status": "ok", "message": f"已追加到: {path}"}


def list_documents(directory: str, workdir: str = "", recursive: bool = True) -> dict:
    """列出目录下的 md/markdown 文件。"""
    root = resolve_path(directory or ".", workdir)
    if not os.path.isdir(root):
        return {"status": "error", "message": f"目录不存在: {root}"}
    root_p = Path(root)
    it = root_p.rglob("*") if recursive else root_p.iterdir()
    files = []
    for p in sorted(it):
        if p.is_file() and p.suffix.lower() in _MD_SUFFIXES:
            files.append(str(p))
    return {
        "status": "ok",
        "directory": root,
        "recursive": bool(recursive),
        "count": len(files),
        "files": files,
    }
