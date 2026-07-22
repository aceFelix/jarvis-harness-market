"""jarvis-harness-xmind — Xmind 思维导图文件操作 harness。

pip 安装后提供全局命令 ``jarvis-harness-xmind``。

安装方式：
    pip install ./harnesses/xmind
    pip install git+https://github.com/aceFelix/jarvis-harness-market.git#subdirectory=harnesses/xmind

@author aceFelix
"""

from setuptools import setup, find_packages

setup(
    name="jarvis-harness-xmind",
    version="1.0.0",
    description="Xmind 思维导图文件操作 harness — 创建/编辑/导出/查看思维导图",
    author="aceFelix",
    python_requires=">=3.11",
    packages=find_packages(include=["jarvis_harness_xmind", "jarvis_harness_xmind.*"]),
    entry_points={
        "console_scripts": [
            "jarvis-harness-xmind=jarvis_harness_xmind.cli:main",
        ],
    },
    # 纯 Python 实现，无外部依赖
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Office/Business",
    ],
)
