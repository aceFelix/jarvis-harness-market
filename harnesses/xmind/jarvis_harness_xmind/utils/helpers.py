"""Xmind 工具函数 — 路径解析、节点路径匹配。

@author aceFelix
"""

from __future__ import annotations

import os
from typing import Any


def resolve_path(path: str, workdir: str = "") -> str:
    """将路径解析为绝对路径。

    支持相对路径（相对于 workdir）、绝对路径、用户目录展开 (~)。
    """
    if not path:
        return ""
    path = os.path.expanduser(path)
    if not os.path.isabs(path) and workdir:
        path = os.path.join(workdir, path)
    return os.path.abspath(path)


def ensure_xmind_ext(path: str) -> str:
    """确保路径以 .xmind 结尾。"""
    if path and not path.lower().endswith(".xmind"):
        path += ".xmind"
    return path


def parse_node_path(node_path: str) -> list[str]:
    """解析节点路径字符串为标题列表。

    支持格式：
    - "根节点>子节点1>子节点2"（用 > 分隔）
    - "根节点/子节点1/子节点2"（用 / 分隔）

    Returns:
        节点标题列表，如 ["根节点", "子节点1", "子节点2"]
    """
    if not node_path:
        return []

    # 优先用 > 分隔
    if ">" in node_path:
        parts = node_path.split(">")
    elif "/" in node_path:
        parts = node_path.split("/")
    else:
        return [node_path.strip()]

    return [p.strip() for p in parts if p.strip()]


def find_node_by_path(root_topic: dict[str, Any], path_parts: list[str]) -> dict[str, Any] | None:
    """根据标题路径在节点树中查找节点。

    Args:
        root_topic: 根节点 dict（含 title, children）
        path_parts: 标题路径列表（第一项应与根节点标题匹配，或跳过根直接匹配子节点）

    Returns:
        找到的节点 dict，或 None
    """
    if not path_parts:
        return root_topic

    # 如果第一项匹配根节点标题，从根开始；否则视为从根的子节点开始
    if path_parts[0] == root_topic.get("title", ""):
        remaining = path_parts[1:]
    else:
        remaining = path_parts

    current = root_topic
    for title in remaining:
        children = _get_children(current)
        found = None
        for child in children:
            if child.get("title", "") == title:
                found = child
                break
        if found is None:
            return None
        current = found

    return current


def find_parent_of(root_topic: dict[str, Any], target_title: str) -> dict[str, Any] | None:
    """查找指定标题节点的父节点（深度优先搜索第一个匹配）。

    Args:
        root_topic: 根节点
        target_title: 要查找父节点的目标标题

    Returns:
        父节点 dict，或 None（如果目标是根节点或未找到）
    """
    children = _get_children(root_topic)
    for child in children:
        if child.get("title", "") == target_title:
            return root_topic
        # 递归
        result = find_parent_of(child, target_title)
        if result is not None:
            return result
    return None


def _get_children(topic: dict[str, Any]) -> list[dict[str, Any]]:
    """获取节点的子节点列表。"""
    children_obj = topic.get("children", {})
    if isinstance(children_obj, dict):
        return children_obj.get("attached", [])
    return []


def collect_all_nodes(topic: dict[str, Any], depth: int = 0) -> list[dict[str, Any]]:
    """递归收集所有节点（含深度信息）。

    Returns:
        [{"title": ..., "id": ..., "depth": ...}, ...]
    """
    result = [{
        "title": topic.get("title", ""),
        "id": topic.get("id", ""),
        "depth": depth,
    }]
    for child in _get_children(topic):
        result.extend(collect_all_nodes(child, depth + 1))
    return result


def count_nodes(topic: dict[str, Any]) -> int:
    """统计节点总数。"""
    count = 1
    for child in _get_children(topic):
        count += count_nodes(child)
    return count
