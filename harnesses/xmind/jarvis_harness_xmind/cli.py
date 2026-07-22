"""jarvis-harness-xmind CLI — Xmind 思维导图文件操作命令行入口。

支持两种调用方式：
1. jarvis runner 格式：jarvis-harness-xmind --action create_map --text "标题" --target path
2. 直接调用格式：    jarvis-harness-xmind --action add_node --target file.xmind --text "节点"

命令列表:
    create_map    创建新导图
    add_node      添加子节点（支持批量）
    edit_node     编辑节点文本
    delete_node   删除节点
    export        导出为 Markdown/文本树
    open          用默认应用打开
    list_nodes    列出所有节点
    info          获取导图信息
    version       显示版本

@author aceFelix
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


# ── 输出工具 ──────────────────────────────────────────────────────────

def _output(data: dict[str, Any]) -> None:
    """以 JSON 格式输出结果，供 jarvis Agent 解析。"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── 操作处理 ─────────────────────────────────────────────────────────

def _do_create_map(args: argparse.Namespace) -> None:
    from jarvis_harness_xmind.core.xmind_file import create_map
    from jarvis_harness_xmind.utils.helpers import resolve_path, ensure_xmind_ext

    target = resolve_path(args.target, args.workdir)
    target = ensure_xmind_ext(target)
    _output(create_map(args.text, target))


def _do_add_node(args: argparse.Namespace) -> None:
    from jarvis_harness_xmind.core.xmind_file import add_node
    from jarvis_harness_xmind.utils.helpers import resolve_path, ensure_xmind_ext

    target = ensure_xmind_ext(resolve_path(args.target, args.workdir))
    _output(add_node(target, args.text, parent_path=args.parent))


def _do_edit_node(args: argparse.Namespace) -> None:
    from jarvis_harness_xmind.core.xmind_file import edit_node
    from jarvis_harness_xmind.utils.helpers import resolve_path, ensure_xmind_ext

    target = ensure_xmind_ext(resolve_path(args.target, args.workdir))
    # node_path 从 --node-path 获取，或回退到 --target 中解析
    node_path = args.node_path or ""
    _output(edit_node(target, node_path, args.text))


def _do_delete_node(args: argparse.Namespace) -> None:
    from jarvis_harness_xmind.core.xmind_file import delete_node
    from jarvis_harness_xmind.utils.helpers import resolve_path, ensure_xmind_ext

    target = ensure_xmind_ext(resolve_path(args.target, args.workdir))
    node_path = args.node_path or ""
    _output(delete_node(target, node_path))


def _do_export(args: argparse.Namespace) -> None:
    from jarvis_harness_xmind.core.xmind_file import export_markdown, export_text_tree
    from jarvis_harness_xmind.utils.helpers import resolve_path, ensure_xmind_ext

    target = ensure_xmind_ext(resolve_path(args.target, args.workdir))
    output_path = resolve_path(args.output_path, args.workdir)

    if not output_path:
        # 默认导出为同目录同名 .md
        output_path = os.path.splitext(target)[0] + ".md"

    fmt = args.format or "md"
    if fmt in ("md", "markdown"):
        if not output_path.endswith(".md"):
            output_path += ".md"
        _output(export_markdown(target, output_path))
    elif fmt in ("txt", "text", "tree"):
        if not output_path.endswith(".txt"):
            output_path += ".txt"
        _output(export_text_tree(target, output_path))
    else:
        _output({"status": "error", "message": f"不支持的导出格式: {fmt}（支持: md, txt）"})


def _do_open(args: argparse.Namespace) -> None:
    from jarvis_harness_xmind.core.xmind_file import open_xmind
    from jarvis_harness_xmind.utils.helpers import resolve_path, ensure_xmind_ext

    target = ensure_xmind_ext(resolve_path(args.target, args.workdir))
    _output(open_xmind(target))


def _do_list_nodes(args: argparse.Namespace) -> None:
    from jarvis_harness_xmind.core.xmind_file import list_nodes
    from jarvis_harness_xmind.utils.helpers import resolve_path, ensure_xmind_ext

    target = ensure_xmind_ext(resolve_path(args.target, args.workdir))
    _output(list_nodes(target))


def _do_info(args: argparse.Namespace) -> None:
    from jarvis_harness_xmind.core.xmind_file import get_map_info
    from jarvis_harness_xmind.utils.helpers import resolve_path, ensure_xmind_ext

    target = ensure_xmind_ext(resolve_path(args.target, args.workdir))
    _output(get_map_info(target))


def _do_version(args: argparse.Namespace) -> None:
    from jarvis_harness_xmind import __version__
    _output({"status": "ok", "version": __version__, "name": "xmind"})


# ── 操作路由 ─────────────────────────────────────────────────────────

_ACTION_MAP = {
    "create_map": _do_create_map,
    "add_node": _do_add_node,
    "edit_node": _do_edit_node,
    "delete_node": _do_delete_node,
    "export": _do_export,
    "open": _do_open,
    "list_nodes": _do_list_nodes,
    "info": _do_info,
    "version": _do_version,
}


# ── 参数解析 ─────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="jarvis-harness-xmind",
        description="Xmind Harness — 思维导图文件操作（创建/编辑/导出/查看）",
    )
    parser.add_argument("--action", required=True,
                        choices=list(_ACTION_MAP.keys()),
                        help="操作类型")
    parser.add_argument("--target", default="", help="文件路径（.xmind）")
    parser.add_argument("--text", default="", help="节点文本/导图标题")
    parser.add_argument("--parent", default="", help="父节点路径（add_node 用，如 '根>子1'）")
    parser.add_argument("--node-path", default="", help="节点路径（edit_node/delete_node 用）")
    parser.add_argument("--output-path", default="", help="导出路径")
    parser.add_argument("--format", default="md", choices=["md", "markdown", "txt", "text", "tree"],
                        help="导出格式（默认 md）")
    parser.add_argument("--harness-dir", default="", help="harness 所在目录")
    parser.add_argument("--workdir", default="", help="当前工作目录")
    parser.add_argument("--json", action="store_true", default=True, help="JSON 输出（默认开启）")
    return parser


# ── 主入口 ───────────────────────────────────────────────────────────

def main() -> None:
    """CLI 主入口。

    调用格式：
        jarvis-harness-xmind --action create_map --text "项目计划" --target plan.xmind
        jarvis-harness-xmind --action add_node --target plan.xmind --text "需求,设计,开发"
        jarvis-harness-xmind --action list_nodes --target plan.xmind
        jarvis-harness-xmind --action export --target plan.xmind --output-path plan.md
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
