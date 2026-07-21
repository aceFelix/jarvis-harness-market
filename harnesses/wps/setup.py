"""jarvis-harness-wps — WPS Office COM 自动化 harness。

pip 安装后提供全局命令 ``jarvis-harness-wps``。

安装方式：
    pip install ./harnesses/wps
    pip install git+https://github.com/<user>/jarvis-harness-market.git#subdirectory=harnesses/wps

@author aceFelix
"""

from setuptools import setup, find_packages

setup(
    name="jarvis-harness-wps",
    version="1.0.0",
    description="WPS Office COM 自动化 harness — 控制 WPS 文字/表格/演示",
    author="aceFelix",
    python_requires=">=3.11",
    packages=find_packages(include=["jarvis_harness_wps", "jarvis_harness_wps.*"]),
    entry_points={
        "console_scripts": [
            "jarvis-harness-wps=jarvis_harness_wps.cli:main",
        ],
    },
    install_requires=[
        "pywin32;platform_system=='Windows'",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Office/Business",
    ],
)
