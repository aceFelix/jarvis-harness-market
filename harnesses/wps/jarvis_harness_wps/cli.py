"""jarvis-harness-wps CLI — WPS Office COM 自动化命令行入口。

支持两种调用方式：
1. jarvis runner 格式：jarvis-harness-wps --subcommand "writer --action open_doc" --json
2. 直接子命令格式：  jarvis-harness-wps writer --action open_doc --target path

命令树:
    writer   open_doc / new_doc / edit_text / save / export_pdf / close / info
    sheet    open_sheet / new_sheet / write_cell / read_cell / write_range / save / export_pdf
    slide    open_presentation / new_presentation / add_slide / save / export_pdf / info
    status   检测 WPS 进程与环境
    version  显示 harness 版本

@author aceFelix
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from typing import Any


# ── 输出工具 ──────────────────────────────────────────────────────────

def _output(data: dict[str, Any]) -> None:
    """以 JSON 格式输出结果，供 jarvis Agent 解析。"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── writer 子命令 ────────────────────────────────────────────────────

def _cmd_writer(args: argparse.Namespace) -> None:
    from jarvis_harness_wps.core import writer

    action = args.writer_action
    workdir = args.workdir or os.getcwd()

    if action == "open_doc":
        if not args.target:
            _output({"status": "error", "message": "缺少 --target 文件路径"})
            return
        _output(writer.open_document(args.target, workdir=workdir, visible=not args.headless))
    elif action == "new_doc":
        _output(writer.new_document(visible=not args.headless))
    elif action == "edit_text":
        if not args.text:
            _output({"status": "error", "message": "缺少 --text 内容"})
            return
        _output(writer.edit_text(args.text, mode=args.mode))
    elif action == "save":
        _output(writer.save_document(file_path=args.output_path, workdir=workdir))
    elif action == "export_pdf":
        if not args.output_path:
            _output({"status": "error", "message": "缺少 --output-path 导出路径"})
            return
        _output(writer.export_pdf(args.output_path, workdir=workdir))
    elif action == "close":
        _output(writer.close_document(save=not args.no_save))
    elif action == "info":
        _output(writer.get_document_info())
    else:
        _output({"status": "error", "message": f"未知 writer 操作: {action}"})


# ── sheet 子命令 ─────────────────────────────────────────────────────

def _cmd_sheet(args: argparse.Namespace) -> None:
    from jarvis_harness_wps.core import spreadsheet

    action = args.sheet_action
    workdir = args.workdir or os.getcwd()

    if action == "open_sheet":
        if not args.target:
            _output({"status": "error", "message": "缺少 --target 文件路径"})
            return
        _output(spreadsheet.open_workbook(args.target, workdir=workdir, visible=not args.headless))
    elif action == "new_sheet":
        _output(spreadsheet.new_workbook(visible=not args.headless))
    elif action == "write_cell":
        if not args.target or not args.text:
            _output({"status": "error", "message": "缺少 --target 单元格地址 或 --text 值"})
            return
        _output(spreadsheet.write_cell(args.target, args.text, sheet_name=args.sheet_name))
    elif action == "read_cell":
        if not args.target:
            _output({"status": "error", "message": "缺少 --target 单元格地址"})
            return
        _output(spreadsheet.read_cell(args.target, sheet_name=args.sheet_name))
    elif action == "write_range":
        if not args.target or not args.data:
            _output({"status": "error", "message": "缺少 --target 起始单元格 或 --data 数据"})
            return
        try:
            data = json.loads(args.data)
            if not isinstance(data, list):
                _output({"status": "error", "message": "--data 必须是二维 JSON 数组"})
                return
        except json.JSONDecodeError as e:
            _output({"status": "error", "message": f"--data JSON 解析失败: {e}"})
            return
        _output(spreadsheet.write_range(args.target, data, sheet_name=args.sheet_name))
    elif action == "save":
        _output(spreadsheet.save_workbook(file_path=args.output_path, workdir=workdir))
    elif action == "export_pdf":
        if not args.output_path:
            _output({"status": "error", "message": "缺少 --output-path 导出路径"})
            return
        _output(spreadsheet.export_pdf(args.output_path, workdir=workdir))
    else:
        _output({"status": "error", "message": f"未知 sheet 操作: {action}"})


# ── slide 子命令 ─────────────────────────────────────────────────────

def _cmd_slide(args: argparse.Namespace) -> None:
    from jarvis_harness_wps.core import presentation

    action = args.slide_action
    workdir = args.workdir or os.getcwd()

    if action == "open_presentation":
        if not args.target:
            _output({"status": "error", "message": "缺少 --target 文件路径"})
            return
        _output(presentation.open_presentation(args.target, workdir=workdir, visible=not args.headless))
    elif action == "new_presentation":
        _output(presentation.new_presentation(visible=not args.headless))
    elif action == "add_slide":
        _output(presentation.add_slide(
            title=args.title or "",
            body=args.text or "",
            layout=args.layout or "text",
        ))
    elif action == "save":
        _output(presentation.save_presentation(file_path=args.output_path, workdir=workdir))
    elif action == "export_pdf":
        if not args.output_path:
            _output({"status": "error", "message": "缺少 --output-path 导出路径"})
            return
        _output(presentation.export_pdf(args.output_path, workdir=workdir))
    elif action == "info":
        _output(presentation.get_presentation_info())
    else:
        _output({"status": "error", "message": f"未知 slide 操作: {action}"})


# ── 全局子命令 ───────────────────────────────────────────────────────

def _cmd_status(args: argparse.Namespace) -> None:
    from jarvis_harness_wps.utils.wps_backend import check_environment, find_wps_processes

    env = check_environment()
    procs = find_wps_processes()
    _output({
        "status": "ok",
        "action": "status",
        "is_windows": env["is_windows"],
        "has_pywin32": env["has_pywin32"],
        "can_run": env["can_run"],
        "wps_running": len(procs) > 0,
        "processes": procs,
    })


def _cmd_version(args: argparse.Namespace) -> None:
    from jarvis_harness_wps import __version__
    _output({"status": "ok", "version": __version__, "name": "wps"})


# ── 子命令解析器构建 ─────────────────────────────────────────────────

def _build_subcommand_parser() -> argparse.ArgumentParser:
    """构建子命令解析器（writer/sheet/slide/status/version）。"""
    parser = argparse.ArgumentParser(
        prog="jarvis-harness-wps",
        description="WPS Office Harness — COM 自动化控制 WPS 文字/表格/演示",
    )
    parser.add_argument("--harness-dir", default="", help="harness 所在目录")
    parser.add_argument("--workdir", default="", help="当前工作目录")
    parser.add_argument("--headless", action="store_true", help="不显示 WPS 窗口")

    sub = parser.add_subparsers(dest="command", help="子命令")

    # writer
    wp = sub.add_parser("writer", help="WPS 文字操作")
    wp.add_argument("--action", dest="writer_action", required=True,
                    choices=["open_doc", "new_doc", "edit_text", "save", "export_pdf", "close", "info"])
    wp.add_argument("--target", default="")
    wp.add_argument("--text", default="")
    wp.add_argument("--mode", default="append", choices=["append", "insert", "replace"])
    wp.add_argument("--output-path", default="")
    wp.add_argument("--no-save", action="store_true")
    wp.add_argument("--headless", action="store_true", help="不显示 WPS 窗口")

    # sheet
    sp = sub.add_parser("sheet", help="WPS 表格操作")
    sp.add_argument("--action", dest="sheet_action", required=True,
                    choices=["open_sheet", "new_sheet", "write_cell", "read_cell", "write_range", "save", "export_pdf"])
    sp.add_argument("--target", default="")
    sp.add_argument("--text", default="")
    sp.add_argument("--data", default="")
    sp.add_argument("--sheet-name", default="")
    sp.add_argument("--output-path", default="")
    sp.add_argument("--headless", action="store_true", help="不显示 WPS 窗口")

    # slide
    slp = sub.add_parser("slide", help="WPS 演示操作")
    slp.add_argument("--action", dest="slide_action", required=True,
                     choices=["open_presentation", "new_presentation", "add_slide", "save", "export_pdf", "info"])
    slp.add_argument("--target", default="")
    slp.add_argument("--title", default="")
    slp.add_argument("--text", default="")
    slp.add_argument("--layout", default="text", choices=["text", "blank"])
    slp.add_argument("--output-path", default="")
    slp.add_argument("--headless", action="store_true", help="不显示 WPS 窗口")

    # status / version
    sub.add_parser("status", help="检测 WPS 进程与环境状态")
    sub.add_parser("version", help="显示 harness 版本")

    return parser


_CMD_MAP = {
    "writer": _cmd_writer,
    "sheet": _cmd_sheet,
    "slide": _cmd_slide,
    "status": _cmd_status,
    "version": _cmd_version,
}


def _dispatch(args: argparse.Namespace) -> None:
    """根据解析后的 args 分发到对应子命令处理函数。"""
    if not getattr(args, "command", None):
        print("jarvis-harness-wps — 用法:")
        print("  jarvis-harness-wps writer --action open_doc --target <path>")
        print("  jarvis-harness-wps sheet  --action new_sheet")
        print("  jarvis-harness-wps slide  --action add_slide --title <title>")
        print("  jarvis-harness-wps status")
        print("  jarvis-harness-wps version")
        print()
        print("jarvis runner 格式:")
        print('  jarvis-harness-wps --subcommand "writer --action open_doc --target report.docx"')
        sys.exit(1)

    handler = _CMD_MAP.get(args.command)
    if handler is None:
        _output({"status": "error", "message": f"未知命令: {args.command}"})
        sys.exit(1)
    handler(args)


# ── 主入口 ───────────────────────────────────────────────────────────

def main() -> None:
    """CLI 主入口，支持两种调用格式。

    格式 1（jarvis runner）：
        jarvis-harness-wps --subcommand "writer --action open_doc" --json --harness-dir ... --workdir ...

    格式 2（直接调用）：
        jarvis-harness-wps writer --action open_doc --target path
    """
    # 先检查是否有 --subcommand 参数（jarvis runner 格式）
    # 用 parse_known_args 提取顶层参数，剩余部分作为子命令
    top_parser = argparse.ArgumentParser(add_help=False)
    top_parser.add_argument("--subcommand", default="", help="子命令字符串（jarvis runner 格式）")
    top_parser.add_argument("--json", action="store_true", default=True, help="JSON 输出（默认开启）")
    top_parser.add_argument("--harness-dir", default="", help="harness 所在目录")
    top_parser.add_argument("--workdir", default="", help="当前工作目录")
    top_parser.add_argument("--headless", action="store_true", default=False, help="不显示 WPS 窗口")

    top_args, remaining = top_parser.parse_known_args()

    if top_args.subcommand:
        # 格式 1：--subcommand "writer --action open_doc --target path"
        sub_argv = shlex.split(top_args.subcommand)
        # 注入全局参数
        if top_args.harness_dir:
            sub_argv.extend(["--harness-dir", top_args.harness_dir])
        if top_args.workdir:
            sub_argv.extend(["--workdir", top_args.workdir])

        parser = _build_subcommand_parser()
        args = parser.parse_args(sub_argv)
        _dispatch(args)
    else:
        # 格式 2：直接子命令 writer --action open_doc ...
        # remaining 包含子命令及其参数
        parser = _build_subcommand_parser()
        # 把顶层已解析的 harness-dir/workdir 注入 remaining
        inject: list[str] = []
        if top_args.harness_dir:
            inject.extend(["--harness-dir", top_args.harness_dir])
        if top_args.workdir:
            inject.extend(["--workdir", top_args.workdir])

        args = parser.parse_args(inject + remaining)
        # 把顶层 --headless 覆盖回子解析结果（子解析器 default 会覆盖主解析器的值）
        if top_args.headless:
            args.headless = True
        _dispatch(args)


if __name__ == "__main__":
    main()
