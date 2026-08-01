"""可用 harness 校验：SKILL.md 解析 + Python 包编译/导入冒烟。

- 所有 harness：SKILL.md frontmatter 必须能被 YAML 解析且字段齐全
- 可用（pip 型，带 install_cmd）harness：所有 .py 编译通过、包可导入、CLI 入口存在

注意：此套件不操作真实软件（Typora/WPS/Xmind），纯静态校验；
真实 GUI 集成验证需在装有对应软件的机器上手动执行。

@author aceFelix
"""

from __future__ import annotations

import importlib
import json
import py_compile
import re
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "registry.json"

# 编译时跳过的目录（构建产物）
_SKIP_DIRS = {"__pycache__", "build", "dist", "*.egg-info"}


def _harnesses() -> list[dict]:
    return json.loads(REGISTRY.read_text(encoding="utf-8")).get("harnesses", [])


def _parse_frontmatter(skill_md: Path) -> dict:
    """解析 SKILL.md 的 YAML frontmatter（--- 分隔的首块）。"""
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---"), f"{skill_md}: 缺少 frontmatter 起始 '---'"
    blocks = text.split("---", 2)
    assert len(blocks) >= 3, f"{skill_md}: frontmatter 格式不完整"
    return yaml.safe_load(blocks[1]) or {}


# ---------------------------------------------------------------------------
# SKILL.md（所有 harness）
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("h", _harnesses(), ids=lambda h: h["id"])
def test_skill_md_parses(h: dict) -> None:
    skill_md = REPO_ROOT / h["skill_md"]
    meta = _parse_frontmatter(skill_md)
    for field in ("name", "id", "description", "command"):
        assert meta.get(field), f"harness '{h['id']}' 的 SKILL.md 缺少字段: {field}"
    assert meta["id"] == h["id"], (
        f"SKILL.md id '{meta['id']}' 与 registry id '{h['id']}' 不一致"
    )


@pytest.mark.parametrize("h", _harnesses(), ids=lambda h: h["id"])
def test_skill_md_args_valid(h: dict) -> None:
    skill_md = REPO_ROOT / h["skill_md"]
    meta = _parse_frontmatter(skill_md)
    args = meta.get("args", [])
    assert isinstance(args, list) and args, f"harness '{h['id']}' 缺少 args 列表"
    for arg in args:
        assert isinstance(arg, dict), f"harness '{h['id']}' 存在非法 arg: {arg}"
        for field in ("name", "type"):
            assert arg.get(field), f"harness '{h['id']}' 的 arg 缺少字段: {field}"


# ---------------------------------------------------------------------------
# pip 型可用 harness：编译 + 导入冒烟
# ---------------------------------------------------------------------------

_PIP_HARNESSES = [h for h in _harnesses() if h.get("install_cmd")]


def test_pip_harnesses_exist() -> None:
    assert _PIP_HARNESSES, "市场中没有带 install_cmd 的可用 harness"
    for h in _PIP_HARNESSES:
        assert h.get("id"), "存在缺少 id 的 harness 条目"


@pytest.mark.parametrize("h", _PIP_HARNESSES, ids=lambda h: h["id"])
def test_all_python_files_compile(h: dict) -> None:
    root = REPO_ROOT / "harnesses" / h["id"]
    py_files = [
        f for f in root.rglob("*.py")
        if not any(part in _SKIP_DIRS or part.endswith(".egg-info") for part in f.parts)
    ]
    assert py_files, f"harness '{h['id']}' 没有任何 .py 文件"
    for f in py_files:
        py_compile.compile(str(f), doraise=True)


@pytest.mark.parametrize("h", _PIP_HARNESSES, ids=lambda h: h["id"])
def test_package_imports_and_cli_entry(h: dict) -> None:
    """包可导入、cli 模块存在且暴露 main 入口。"""
    root = REPO_ROOT / "harnesses" / h["id"]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    pkg_name = f"jarvis_harness_{h['id']}"
    pkg = importlib.import_module(pkg_name)
    assert getattr(pkg, "__version__", None), f"{pkg_name} 缺少 __version__"
    cli = importlib.import_module(f"{pkg_name}.cli")
    assert callable(getattr(cli, "main", None)), f"{pkg_name}.cli 缺少 main()"
