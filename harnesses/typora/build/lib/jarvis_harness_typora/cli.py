"""jarvis-harness-typora CLI — Typora Markdown 编辑器操作命令行入口。

支持两种调用方式：
1. jarvis runner 格式：jarvis-harness-typora --action open --target "D:\\docs\\readme.md" --json
2. 直接调用格式：    jarvis-harness-typora --action read --target "D:\\docs\\readme.md"

命令列表:
    open      在 Typora 中打开文档（不存在自动创建）
    create    新建文档并打开
    read      读取文档内容
    write     写入/覆盖文档
    append    追加内容到文档
    list      列出目录下的 md/markdown 文件
    info      检测 Typora 环境
    version   显示版本

@author aceFelix
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

# Windows 控制台默认 GBK，JSON 含中文/emoji 时会 UnicodeEncodeError
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ── 输出工具 ──────────────────────────────────────────────────────────

def _output(data: dict[str, Any]) -> None:
    """以 JSON 格式输出结果，供 jarvis Agent 解析。"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── 操作处理 ─────────────────────────────────────────────────────────

def _do_open(args: argparse.Namespace) -> None:
    from jarvis_harness_typora.core import document
    from jarvis_harness_typora.utils import typora_app

    exe = typora_app.find_typora_exe()
    if exe is None:
        _output({"status": "error", "message": "未找到 Typora，请确认已安装"})
        return
    if args.target:
        path = document.ensure_md_ext(document.resolve_path(args.target, args.workdir))
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8"):
                pass
        typora_app.open_in_typora(exe, path)
        _output({"status": "ok", "message": f"已在 Typora 打开: {path}"})
    else:
        typora_app.open_in_typora(exe)
        _output({"status": "ok", "message": "已启动 Typora"})


def _do_create(args: argparse.Namespace) -> None:
    from jarvis_harness_typora.core import document
    from jarvis_harness_typora.utils import typora_app

    path = document.ensure_md_ext(document.resolve_path(args.target, args.workdir))
    if os.path.exists(path):
        _output({"status": "error", "message": f"文件已存在: {path}"})
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(args.content or "")
    exe = typora_app.find_typora_exe()
    if exe:
        typora_app.open_in_typora(exe, path)
        _output({"status": "ok", "message": f"已创建并在 Typora 打开: {path}"})
    else:
        _output({"status": "ok", "message": f"已创建: {path}（未安装 Typora，未打开）"})


def _do_read(args: argparse.Namespace) -> None:
    from jarvis_harness_typora.core import document

    path = document.ensure_md_ext(document.resolve_path(args.target, args.workdir))
    _output(document.read_document(path))


def _do_write(args: argparse.Namespace) -> None:
    from jarvis_harness_typora.core import document

    if not args.content:
        _output({"status": "error", "message": "write 操作缺少 --content 内容"})
        return
    path = document.ensure_md_ext(document.resolve_path(args.target, args.workdir))
    _output(document.write_document(path, args.content))


def _do_append(args: argparse.Namespace) -> None:
    from jarvis_harness_typora.core import document

    if not args.content:
        _output({"status": "error", "message": "append 操作缺少 --content 内容"})
        return
    path = document.ensure_md_ext(document.resolve_path(args.target, args.workdir))
    _output(document.append_document(path, args.content))


def _do_list(args: argparse.Namespace) -> None:
    from jarvis_harness_typora.core import document

    _output(document.list_documents(args.directory, args.workdir, recursive=args.recursive))


def _do_info(args: argparse.Namespace) -> None:
    from jarvis_harness_typora.utils import typora_app

    _output({"status": "ok", "action": "info", **typora_app.get_environment()})


def _do_version(args: argparse.Namespace) -> None:
    from jarvis_harness_typora import __version__

    _output({"status": "ok", "version": __version__, "name": "typora"})


# ── 操作路由 ─────────────────────────────────────────────────────────

_ACTION_MAP = {
    "open": _do_open,
    "create": _do_create,
    "read": _do_read,
    "write": _do_write,
    "append": _do_append,
    "list": _do_list,
    "info": _do_info,
    "version": _do_version,
}


# ── 参数解析 ─────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="jarvis-harness-typora",
        description="Typora Harness — Markdown 编辑器文件操作（打开/新建/读写/列出）",
    )
    parser.add_argument("--action", required=True,
                        choices=list(_ACTION_MAP.keys()),
                        help="操作类型")
    parser.add_argument("--target", default="", help="目标 .md 文件路径")
    parser.add_argument("--content", default="", help="要写入/追加的内容")
    parser.add_argument("--directory", default="", help="list 用：要扫描的目录")
    parser.add_argument("--recursive", action="store_true", help="list 用：递归扫描子目录")
    parser.add_argument("--harness-dir", default="", help="harness 所在目录")
    parser.add_argument("--workdir", default="", help="当前工作目录")
    parser.add_argument("--json", action="store_true", default=True, help="JSON 输出（默认开启）")
    return parser


# ── 主入口 ───────────────────────────────────────────────────────────

def main() -> None:
    """CLI 主入口。

    调用格式：
        jarvis-harness-typora --action open --target "D:\\docs\\readme.md"
        jarvis-harness-typora --action create --target note.md --content "# 标题"
        jarvis-harness-typora --action read --target "D:\\docs\\readme.md"
        jarvis-harness-typora --action write --target note.md --content "新内容"
        jarvis-harness-typora --action append --target note.md --content "追加段"
        jarvis-harness-typora --action list --directory "D:\\docs"
        jarvis-harness-typora --action info
    """
    parser = _build_parser()
    args = parser.parse_args()

    handler = _ACTION_MAP.get(args.action)
    if handler is None:
        _output({"status": "error", "message": f"未知操作: {args.action}"})
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
