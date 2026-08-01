"""registry.json 市场注册表校验。

确保注册表配置合法、路径存在、install_cmd 与 harness 目录一致——
市场发布前最常见的问题（拼写错误、路径缺失、目录改名）都在这里拦住。

@author aceFelix
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "registry.json"


def _load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _harnesses() -> list[dict]:
    return _load_registry().get("harnesses", [])


def test_registry_is_valid_json() -> None:
    assert REGISTRY.is_file(), f"缺少 {REGISTRY.name}"
    data = _load_registry()
    assert isinstance(data, dict)
    assert data.get("name") == "jarvis-harness-market"
    assert "harnesses" in data


def test_harness_ids_are_unique() -> None:
    ids = [h["id"] for h in _harnesses()]
    assert len(ids) == len(set(ids)), f"存在重复 id: {ids}"


def test_required_fields_present() -> None:
    required = {"id", "display_name", "description", "skill_md"}
    for h in _harnesses():
        missing = required - h.keys()
        assert not missing, f"harness '{h.get('id')}' 缺少字段: {missing}"


def test_skill_md_paths_exist() -> None:
    for h in _harnesses():
        path = REPO_ROOT / h["skill_md"]
        assert path.is_file(), f"harness '{h['id']}' 的 skill_md 不存在: {h['skill_md']}"


def test_install_cmd_matches_id_and_subdir() -> None:
    """install_cmd 的 #subdirectory 必须指向 harnesses/<id>，且目录存在。"""
    for h in _harnesses():
        cmd = h.get("install_cmd", "")
        if not cmd:
            continue
        pattern = r"subdirectory=harnesses/([\w-]+)"
        match = re.search(pattern, cmd)
        assert match, f"harness '{h['id']}' 的 install_cmd 缺少 #subdirectory=harnesses/<id>"
        assert match.group(1) == h["id"], (
            f"harness '{h['id']}' 的 install_cmd subdirectory 与 id 不一致: {cmd}"
        )
        assert (REPO_ROOT / "harnesses" / h["id"]).is_dir(), (
            f"harness 目录不存在: harnesses/{h['id']}"
        )


def test_pip_harnesses_have_setup_and_package() -> None:
    """带 install_cmd 的 harness（pip 型）必须有 setup.py 和 jarvis_harness_<id> 包。"""
    for h in _harnesses():
        if not h.get("install_cmd"):
            continue
        root = REPO_ROOT / "harnesses" / h["id"]
        assert (root / "setup.py").is_file(), f"harness '{h['id']}' 缺少 setup.py"
        pkg = root / f"jarvis_harness_{h['id']}"
        assert (pkg / "__init__.py").is_file(), f"harness '{h['id']}' 缺少包 {pkg.name}/"
