#!/usr/bin/env python3
"""WPS Office Harness — 向后兼容入口。

pip 安装后请使用全局命令 ``jarvis-harness-wps``。
此文件保留是为了兼容 jarvis 的目录复制安装方式（python run.py ...）。

@author aceFelix
"""

from __future__ import annotations

import os
import sys

# 将 harness 目录加入 sys.path，使 jarvis_harness_wps 包可被导入
_HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
if _HARNESS_DIR not in sys.path:
    sys.path.insert(0, _HARNESS_DIR)

from jarvis_harness_wps.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
