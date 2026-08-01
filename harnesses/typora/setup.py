"""jarvis-harness-typora — Typora Markdown 编辑器 harness。

pip 安装后提供全局命令 ``jarvis-harness-typora``。

安装方式：
    pip install ./harnesses/typora
    pip install git+https://github.com/aceFelix/jarvis-harness-market.git#subdirectory=harnesses/typora

@author aceFelix
"""

from setuptools import setup, find_packages

setup(
    name="jarvis-harness-typora",
    version="1.0.0",
    description="Typora Markdown 编辑器 harness — 打开/新建/读写 md 文档",
    author="aceFelix",
    python_requires=">=3.11",
    packages=find_packages(include=["jarvis_harness_typora", "jarvis_harness_typora.*"]),
    entry_points={
        "console_scripts": [
            "jarvis-harness-typora=jarvis_harness_typora.cli:main",
        ],
    },
    # 纯 Python 文件操作，无外部依赖（Typora 自动保存，无需 GUI 自动化库）
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup",
    ],
)
