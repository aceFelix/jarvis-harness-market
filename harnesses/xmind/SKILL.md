---
name: Xmind
id: xmind
description: 通过文件操作控制 Xmind 思维导图（创建导图、添加节点、编辑节点、删除节点、导出 Markdown、打开导图）
when_to_use: 用户需要创建或编辑 Xmind 思维导图、添加/修改/删除节点、导出导图或查看导图结构时
trigger_words: [xmind, 思维导图, 脑图, 导图, 节点, mindmap]
command: jarvis-harness-xmind
args:
  - name: action
    type: string
    required: true
    enum: [create_map, add_node, edit_node, delete_node, export, open, list_nodes, info, version]
    description: "操作类型：create_map=创建新导图, add_node=添加子节点(支持批量), edit_node=编辑节点文本, delete_node=删除节点, export=导出为Markdown/文本树, open=用默认应用打开, list_nodes=列出所有节点, info=获取导图信息, version=版本"
  - name: target
    type: string
    required: false
    description: "文件路径（.xmind 文件）。create_map 时为保存路径，其他操作为要操作的导图文件路径"
  - name: text
    type: string
    required: false
    description: "文本内容。create_map 时为导图标题，add_node 时为节点文字（逗号/分号分隔可批量添加），edit_node 时为新文本"
  - name: parent
    type: string
    required: false
    description: "父节点路径（add_node 用，格式: '根节点>子节点1'，默认添加到根节点下）"
  - name: node-path
    type: string
    required: false
    description: "节点路径（edit_node/delete_node 用，格式: '根节点>子节点1>子节点2'）"
  - name: output-path
    type: string
    required: false
    description: "导出路径（export 用，不指定则默认同目录同名 .md）"
  - name: format
    type: string
    required: false
    enum: [md, markdown, txt, text, tree]
    description: "导出格式（默认 md=Markdown，txt=纯文本树）"
  - name: max_depth
    type: integer
    required: false
    default: 0
    description: "list_nodes/export 时限制输出深度（0=不限制，1=仅根节点，2=根+一级子节点...）。节点多时建议设 2-3 避免输出过长"
examples:
  - "jarvis-harness-xmind --action create_map --text 项目计划 --target C:\\Users\\me\\plan.xmind"
  - "jarvis-harness-xmind --action add_node --target C:\\Users\\me\\plan.xmind --text 需求,设计,开发,测试"
  - "jarvis-harness-xmind --action add_node --target plan.xmind --text 前端,后端 --parent 项目计划>设计"
  - "jarvis-harness-xmind --action edit_node --target plan.xmind --node-path 项目计划>需求 --text 需求分析"
  - "jarvis-harness-xmind --action delete_node --target plan.xmind --node-path 项目计划>测试"
  - "jarvis-harness-xmind --action list_nodes --target C:\\Users\\me\\plan.xmind"
  - "jarvis-harness-xmind --action export --target plan.xmind --output-path plan.md --format md"
  - "jarvis-harness-xmind --action open --target C:\\Users\\me\\plan.xmind"
---

# Xmind Harness

通过文件操作控制 Xmind 思维导图（.xmind 文件本质是 ZIP 包含 JSON），纯 Python 实现，无需启动 Xmind 应用。

## 安装

```bash
pip install jarvis-harness-xmind
```

## 命令列表

```
jarvis-harness-xmind --action <action> [options]

  create_map     创建新导图        --text <标题> --target <保存路径>
  add_node       添加子节点        --target <文件> --text <节点文字> [--parent <父路径>]
  edit_node      编辑节点文本      --target <文件> --node-path <节点路径> --text <新文字>
  delete_node    删除节点          --target <文件> --node-path <节点路径>
  export         导出为 MD/TXT    --target <文件> [--output-path <路径>] [--format md|txt]
  open           用默认应用打开    --target <文件>
  list_nodes     列出所有节点      --target <文件>
  info           获取导图信息      --target <文件>
  version        显示版本
```

## 节点路径格式

用 `>` 或 `/` 分隔层级：
- `项目计划>设计>前端` — 从根节点"项目计划"下的"设计"下的"前端"
- `设计>前端` — 省略根节点，直接从子节点开始匹配

## 批量添加节点

`--text` 支持逗号、分号、换行分隔：
```bash
jarvis-harness-xmind --action add_node --target plan.xmind --text "需求,设计,开发,测试"
```
一次添加 4 个同级子节点。

## 前置条件

- **纯 Python 实现**，无外部依赖
- 导出 PNG/PDF 需安装 Xmind 应用（本 harness 仅支持导出 Markdown/文本树）
- `open` 操作需系统已安装 Xmind 应用

## 技术原理

.xmind 文件是 ZIP 压缩包，内结构：
- `content.json` — 导图节点树（JSON 格式）
- `metadata.json` — 元数据
- `manifest.json` — 文件清单

本 harness 直接操作 ZIP 内的 JSON 实现增删改查，无需启动 Xmind 应用。
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
