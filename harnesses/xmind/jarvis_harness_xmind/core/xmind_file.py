"""Xmind 文件操作核心 — 创建、读取、修改 .xmind ZIP 文件。

.xmind 文件本质是 ZIP 压缩包，内含：
- content.json — 导图节点树（JSON 数组，每项为一个 sheet）
- metadata.json — 元数据（创建者信息）
- manifest.json — 文件清单

本模块直接操作 ZIP 内 JSON，无需启动 Xmind 应用。

@author aceFelix
"""

from __future__ import annotations

import json
import os
import uuid
import zipfile
from typing import Any

from jarvis_harness_xmind.utils.helpers import (
    _get_children,
    collect_all_nodes,
    count_nodes,
    find_node_by_path,
    find_parent_of,
    parse_node_path,
)


# ── ID 生成 ──────────────────────────────────────────────────────────

def _gen_id() -> str:
    """生成 Xmind 风格的唯一 ID。"""
    return uuid.uuid4().hex[:26]


# ── 文件读写 ─────────────────────────────────────────────────────────

def _read_xmind(file_path: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """读取 .xmind 文件，返回 (content, metadata)。

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件格式无效
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            # 读取 content.json
            if "content.json" not in zf.namelist():
                raise ValueError(f"无效的 .xmind 文件（缺少 content.json）: {file_path}")
            content = json.loads(zf.read("content.json").decode("utf-8"))

            # 读取 metadata.json（可选）
            metadata: dict[str, Any] = {}
            if "metadata.json" in zf.namelist():
                metadata = json.loads(zf.read("metadata.json").decode("utf-8"))

            return content, metadata
    except zipfile.BadZipFile:
        raise ValueError(f"文件不是有效的 ZIP/Xmind 格式: {file_path}")


def _write_xmind(file_path: str, content: list[dict[str, Any]], metadata: dict[str, Any] | None = None) -> None:
    """将 content 和 metadata 写入 .xmind ZIP 文件。"""
    if metadata is None:
        metadata = {
            "creator": {
                "name": "jarvis-harness-xmind",
                "version": "1.0.0",
            }
        }

    manifest = {
        "file-entries": {
            "content.json": {},
            "metadata.json": {},
        }
    }

    # 确保目录存在
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", json.dumps(content, ensure_ascii=False, indent=2))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))


def _get_root_topic(content: list[dict[str, Any]], sheet_index: int = 0) -> dict[str, Any]:
    """获取指定 sheet 的根节点。"""
    if not content or sheet_index >= len(content):
        raise ValueError(f"导图没有有效的 sheet（index={sheet_index}）")
    sheet = content[sheet_index]
    root = sheet.get("rootTopic")
    if not root:
        raise ValueError("sheet 缺少 rootTopic")
    return root


# ── 公开操作 ─────────────────────────────────────────────────────────

def create_map(title: str, file_path: str) -> dict[str, Any]:
    """创建新的 .xmind 思维导图文件。

    Args:
        title: 根节点标题（导图主题）
        file_path: 保存路径（.xmind）

    Returns:
        操作结果字典
    """
    if not title:
        return {"status": "error", "message": "缺少导图标题（text 参数）"}
    if not file_path:
        return {"status": "error", "message": "缺少保存路径（target 参数）"}

    root_topic = {
        "id": _gen_id(),
        "class": "topic",
        "title": title,
        "structureClass": "org.xmind.ui.map.unbalanced",
        "children": {"attached": []},
    }

    content = [{
        "id": _gen_id(),
        "class": "sheet",
        "title": "画布 1",
        "rootTopic": root_topic,
    }]

    try:
        _write_xmind(file_path, content)
        return {
            "status": "ok",
            "action": "create_map",
            "file_path": file_path,
            "title": title,
            "message": f"已创建思维导图: {title}",
        }
    except Exception as e:
        return {"status": "error", "message": f"创建导图失败: {e}"}


def add_node(file_path: str, text: str, parent_path: str = "") -> dict[str, Any]:
    """在指定父节点下添加子节点。

    Args:
        file_path: .xmind 文件路径
        text: 新节点文本（支持逗号/分号分隔批量添加）
        parent_path: 父节点路径（如 "根节点>子节点1"），为空则添加到根节点下

    Returns:
        操作结果字典
    """
    if not text:
        return {"status": "error", "message": "缺少节点文本（text 参数）"}

    try:
        content, metadata = _read_xmind(file_path)
        root = _get_root_topic(content)

        # 确定父节点
        if parent_path:
            path_parts = parse_node_path(parent_path)
            parent = find_node_by_path(root, path_parts)
            if parent is None:
                return {"status": "error", "message": f"找不到父节点: {parent_path}"}
        else:
            parent = root

        # 支持批量添加（逗号或分号分隔）
        titles = _split_titles(text)
        added = []

        for t in titles:
            new_node = {
                "id": _gen_id(),
                "class": "topic",
                "title": t,
            }
            # 确保 children 结构存在
            if "children" not in parent:
                parent["children"] = {"attached": []}
            elif "attached" not in parent.get("children", {}):
                parent["children"]["attached"] = []
            parent["children"]["attached"].append(new_node)
            added.append(t)

        _write_xmind(file_path, content, metadata)
        return {
            "status": "ok",
            "action": "add_node",
            "file_path": file_path,
            "parent": parent.get("title", ""),
            "added_nodes": added,
            "count": len(added),
            "total_nodes": count_nodes(root),
        }
    except (FileNotFoundError, ValueError) as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"添加节点失败: {e}"}


def edit_node(file_path: str, node_path: str, new_text: str) -> dict[str, Any]:
    """修改指定节点的文本。

    Args:
        file_path: .xmind 文件路径
        node_path: 节点路径（如 "根节点>子节点1"）
        new_text: 新文本

    Returns:
        操作结果字典
    """
    if not node_path:
        return {"status": "error", "message": "缺少节点路径（target 参数，格式: '根节点>子节点'）"}
    if not new_text:
        return {"status": "error", "message": "缺少新文本（text 参数）"}

    try:
        content, metadata = _read_xmind(file_path)
        root = _get_root_topic(content)

        path_parts = parse_node_path(node_path)
        node = find_node_by_path(root, path_parts)
        if node is None:
            return {"status": "error", "message": f"找不到节点: {node_path}"}

        old_title = node.get("title", "")
        node["title"] = new_text

        _write_xmind(file_path, content, metadata)
        return {
            "status": "ok",
            "action": "edit_node",
            "file_path": file_path,
            "old_title": old_title,
            "new_title": new_text,
        }
    except (FileNotFoundError, ValueError) as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"编辑节点失败: {e}"}


def delete_node(file_path: str, node_path: str) -> dict[str, Any]:
    """删除指定节点及其子树。

    Args:
        file_path: .xmind 文件路径
        node_path: 节点路径

    Returns:
        操作结果字典
    """
    if not node_path:
        return {"status": "error", "message": "缺少节点路径（target 参数）"}

    try:
        content, metadata = _read_xmind(file_path)
        root = _get_root_topic(content)

        path_parts = parse_node_path(node_path)

        # 不允许删除根节点
        if not path_parts or (len(path_parts) == 1 and path_parts[0] == root.get("title", "")):
            return {"status": "error", "message": "不能删除根节点"}

        # 找到目标节点的标题
        target_title = path_parts[-1]

        # 找到父节点
        parent = find_parent_of(root, target_title)
        if parent is None:
            return {"status": "error", "message": f"找不到节点: {node_path}"}

        # 从父节点的 children 中移除
        children = _get_children(parent)
        original_len = len(children)
        parent["children"]["attached"] = [
            c for c in children if c.get("title", "") != target_title
        ]
        removed_count = original_len - len(parent["children"]["attached"])

        if removed_count == 0:
            return {"status": "error", "message": f"找不到节点: {node_path}"}

        _write_xmind(file_path, content, metadata)
        return {
            "status": "ok",
            "action": "delete_node",
            "file_path": file_path,
            "deleted": target_title,
            "total_nodes": count_nodes(root),
        }
    except (FileNotFoundError, ValueError) as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"删除节点失败: {e}"}


def list_nodes(file_path: str) -> dict[str, Any]:
    """列出导图所有节点（树形结构）。

    Args:
        file_path: .xmind 文件路径

    Returns:
        操作结果字典（含节点树）
    """
    try:
        content, _ = _read_xmind(file_path)
        root = _get_root_topic(content)

        nodes = collect_all_nodes(root)
        # 构建树形文本
        tree_lines = []
        for n in nodes:
            indent = "  " * n["depth"]
            prefix = "├── " if n["depth"] > 0 else ""
            tree_lines.append(f"{indent}{prefix}{n['title']}")

        return {
            "status": "ok",
            "action": "list_nodes",
            "file_path": file_path,
            "root_title": root.get("title", ""),
            "total_nodes": len(nodes),
            "tree": "\n".join(tree_lines),
            "nodes": nodes,
        }
    except (FileNotFoundError, ValueError) as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"列出节点失败: {e}"}


def export_markdown(file_path: str, output_path: str) -> dict[str, Any]:
    """将导图导出为 Markdown 格式。

    Args:
        file_path: .xmind 文件路径
        output_path: 输出 .md 文件路径

    Returns:
        操作结果字典
    """
    try:
        content, _ = _read_xmind(file_path)
        root = _get_root_topic(content)

        nodes = collect_all_nodes(root)
        lines = [f"# {root.get('title', '思维导图')}\n"]

        for n in nodes[1:]:  # 跳过根节点（已作为标题）
            indent = "  " * (n["depth"] - 1)
            lines.append(f"{indent}- {n['title']}")

        md_content = "\n".join(lines) + "\n"

        # 确保目录存在
        dir_path = os.path.dirname(output_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return {
            "status": "ok",
            "action": "export",
            "format": "markdown",
            "file_path": file_path,
            "output_path": output_path,
            "total_nodes": len(nodes),
        }
    except (FileNotFoundError, ValueError) as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"导出 Markdown 失败: {e}"}


def export_text_tree(file_path: str, output_path: str) -> dict[str, Any]:
    """将导图导出为纯文本树形结构。

    Args:
        file_path: .xmind 文件路径
        output_path: 输出 .txt 文件路径

    Returns:
        操作结果字典
    """
    try:
        content, _ = _read_xmind(file_path)
        root = _get_root_topic(content)

        nodes = collect_all_nodes(root)
        lines = []
        for n in nodes:
            indent = "│   " * n["depth"]
            if n["depth"] == 0:
                lines.append(n["title"])
            else:
                lines.append(f"{indent}├── {n['title']}")

        tree_content = "\n".join(lines) + "\n"

        dir_path = os.path.dirname(output_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(tree_content)

        return {
            "status": "ok",
            "action": "export",
            "format": "text_tree",
            "file_path": file_path,
            "output_path": output_path,
            "total_nodes": len(nodes),
        }
    except (FileNotFoundError, ValueError) as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"导出文本树失败: {e}"}


def open_xmind(file_path: str) -> dict[str, Any]:
    """用系统默认应用打开 .xmind 文件。

    Args:
        file_path: .xmind 文件路径

    Returns:
        操作结果字典
    """
    if not os.path.isfile(file_path):
        return {"status": "error", "message": f"文件不存在: {file_path}"}

    try:
        import sys
        if sys.platform == "win32":
            os.startfile(file_path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            import subprocess
            subprocess.Popen(["open", file_path])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", file_path])

        return {
            "status": "ok",
            "action": "open",
            "file_path": file_path,
            "message": f"已用默认应用打开: {os.path.basename(file_path)}",
        }
    except Exception as e:
        return {"status": "error", "message": f"打开文件失败: {e}"}


def get_map_info(file_path: str) -> dict[str, Any]:
    """获取导图基本信息。

    Args:
        file_path: .xmind 文件路径

    Returns:
        操作结果字典
    """
    try:
        content, metadata = _read_xmind(file_path)
        root = _get_root_topic(content)

        return {
            "status": "ok",
            "action": "info",
            "file_path": file_path,
            "root_title": root.get("title", ""),
            "sheet_count": len(content),
            "total_nodes": count_nodes(root),
            "creator": metadata.get("creator", {}).get("name", "unknown"),
        }
    except (FileNotFoundError, ValueError) as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"获取导图信息失败: {e}"}


# ── 辅助 ─────────────────────────────────────────────────────────────

def _split_titles(text: str) -> list[str]:
    """将文本按逗号/分号/换行分割为多个标题（批量添加用）。"""
    import re
    # 按中文逗号、英文逗号、中文分号、英文分号、换行分割
    parts = re.split(r"[,，;；\n]+", text)
    return [p.strip() for p in parts if p.strip()]
