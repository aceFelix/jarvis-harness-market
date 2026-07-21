#!/usr/bin/env python3
"""QQ Harness 执行入口。

通过 pywinauto + pyautogui 控制 QQ 桌面客户端。
当前为框架版本，具体控制逻辑待实现。

@author aceFelix
"""

from __future__ import annotations

import argparse
import json
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="QQ Harness")
    p.add_argument("--action", required=True,
                   choices=["send_msg", "read_msgs", "search_contact", "screenshot", "list_contacts"],
                   help="操作类型")
    p.add_argument("--target", default="", help="操作对象（联系人/群名）")
    p.add_argument("--message", default="", help="要发送的消息内容")
    p.add_argument("--count", type=int, default=10, help="读取消息数量")
    p.add_argument("--harness-dir", default="", help="harness 所在目录")
    p.add_argument("--workdir", default="", help="当前工作目录")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # TODO: 实现具体控制逻辑
    # - send_msg: pywinauto 定位 QQ 窗口 → 搜索联系人 → 输入消息 → 发送
    # - read_msgs: 定位聊天窗口 → 读取消息列表控件文本
    # - search_contact: Ctrl+F 搜索 → 返回结果
    # - screenshot: pyautogui 截取 QQ 窗口区域 → 保存为 PNG
    # - list_contacts: 读取联系人列表控件

    result = {
        "status": "not_implemented",
        "action": args.action,
        "target": args.target,
        "message": f"QQ harness '{args.action}' 尚未实现，敬请期待。",
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
