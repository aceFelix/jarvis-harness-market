---
name: Xmind
id: xmind
description: 通过文件操作控制 Xmind 思维导图（创建导图、添加节点、编辑节点、导出、打开）
when_to_use: 用户需要创建或编辑 Xmind 思维导图、添加/修改节点、导出导图或打开已有导图时
trigger_words: [xmind, 思维导图, 脑图, 导图, 节点]
command: python
args:
  - name: action
    type: string
    required: true
    enum: [create_map, add_node, edit_node, delete_node, export, open, list_nodes]
    description: "操作类型：create_map=创建新导图, add_node=添加子节点, edit_node=编辑节点文本, delete_node=删除节点, export=导出为PNG/PDF/Markdown, open=打开已有导图, list_nodes=列出所有节点"
  - name: target
    type: string
    required: false
    description: "操作对象（文件路径 或 节点ID/路径如 '根节点>子节点1'）"
  - name: text
    type: string
    required: false
    description: "节点文本内容（create_map 时为导图标题，add_node/edit_node 时为节点文字）"
  - name: output_path
    type: string
    required: false
    description: "导出路径（action=export 时必填，支持 .png/.pdf/.md）"
  - name: parent
    type: string
    required: false
    description: "父节点路径（action=add_node 时指定在哪个节点下添加，默认根节点）"
examples:
  - "创建一个 Xmind 思维导图，标题是'项目计划'"
  - "在'项目计划'导图的根节点下添加三个子节点：需求、设计、开发"
  - "把导图导出为 PNG 图片"
  - "打开桌面上的脑图.xmind，列出所有节点"
---

# Xmind Harness

通过文件操作控制 Xmind 思维导图（.xmind 文件本质是 ZIP 包含 JSON）。

## 支持的操作

| action | 说明 | 必填参数 |
|--------|------|----------|
| create_map | 创建新导图文件 | text(标题), target(保存路径) |
| add_node | 在指定父节点下添加子节点 | target(文件路径), text(节点文字), parent(可选) |
| edit_node | 修改指定节点的文本 | target(文件路径+节点路径), text(新文字) |
| delete_node | 删除指定节点及其子树 | target(文件路径+节点路径) |
| export | 导出为 PNG/PDF/Markdown | target(文件路径), output_path |
| open | 用 Xmind 应用打开导图 | target(文件路径) |
| list_nodes | 列出导图所有节点树 | target(文件路径) |

## 前置条件

- 已安装 Xmind 应用（open 操作需要）
- 纯 Python 实现文件读写（无需额外依赖）
- 导出 PNG/PDF 需要 Xmind 应用或 LibreOffice

## 使用方式

```bash
python run.py --action create_map --text "项目计划" --target "C:\Users\me\plan.xmind" --harness-dir <dir> --workdir <dir>
```

## 技术原理

.xmind 文件是 ZIP 压缩包，内部结构：
- `content.json` — 导图节点树（JSON 格式）
- `metadata.json` — 元数据
- `manifest.json` — 文件清单

本 harness 直接操作 ZIP 内的 JSON 实现增删改查，无需启动 Xmind 应用。
