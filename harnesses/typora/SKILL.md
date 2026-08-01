---
name: Typora
id: typora
description: 控制 Typora Markdown 编辑器（打开/新建文档、读写 md 文件内容、列出文档、环境检测）
when_to_use: 用户需要用 Typora 打开、创建、编辑或查看 Markdown 文档，或需要读写 .md 笔记文件时
trigger_words: [typora, markdown, md 文档, 笔记, md 文件, 编辑器]
command: jarvis-harness-typora
args:
  - name: action
    type: string
    required: true
    enum: [open, create, read, write, append, list, info, version]
    description: "操作类型：open=在 Typora 打开文档(不存在自动创建), create=新建文档并打开, read=读取文档内容, write=写入/覆盖文档, append=追加内容到文档, list=列出目录下的 md 文档, info=检测 Typora 环境, version=版本"
  - name: target
    type: string
    required: false
    description: "目标 .md 文件路径（open/create/read/write/append 用；相对路径基于工作目录，无后缀自动补 .md）"
  - name: content
    type: string
    required: false
    description: "要写入/追加的内容（write/append 必填；create 可选作为初始内容）"
  - name: directory
    type: string
    required: false
    description: "list 用：要扫描的目录（默认工作目录）"
  - name: recursive
    type: boolean
    default: true
    description: "list 用：是否递归扫描子目录"
examples:
  - "jarvis-harness-typora --action open --target C:\\Users\\me\\readme.md"
  - "jarvis-harness-typora --action create --target docs\\note.md --content # 项目计划"
  - "jarvis-harness-typora --action read --target C:\\Users\\me\\readme.md"
  - "jarvis-harness-typora --action write --target note.md --content 新内容"
  - "jarvis-harness-typora --action append --target docs\\meeting-2026.md --content 会议结论"
  - "jarvis-harness-typora --action list --directory C:\\Users\\me\\docs"
  - "jarvis-harness-typora --action info"
---

# Typora Harness

通过「文件读写 + 启动应用」控制 Typora Markdown 编辑器。

## 安装

```bash
pip install jarvis-harness-typora
```

## 命令列表

```
jarvis-harness-typora --action <action> [options]

  open      在 Typora 打开文档    --target <路径>（不存在自动创建）
  create    新建文档并打开        --target <路径> [--content <初始内容>]
  read      读取文档内容          --target <路径>
  write     写入/覆盖文档         --target <路径> --content <内容>
  append    追加内容到文档末尾    --target <路径> --content <内容>
  list      列出 md 文件          [--directory <目录>] [--recursive]
  info      检测 Typora 环境
  version   显示版本
```

## 设计要点

- **文件操作优先**：read/write/append/list 直接读写 `.md` 文件，纯 Python、
  跨平台稳健，不依赖 Typora 的打开状态（Typora 自动保存，文件即真相）。
- **打开操作**：open/create 自动探测 Typora 可执行文件（环境变量 → PATH → 注册表 → 常见路径），
  分离进程启动，不阻塞调用方。
- **无需手动保存**：Typora 默认自动保存，未提供 save/close 操作。

## 前置条件

- 已安装 Typora（`open`/`create` 需要；`read`/`write`/`append`/`list` 不需要）
- 纯 Python 文件操作，无外部依赖

## 自动定位 Typora

无需配置，harness 按以下顺序自动查找 Typora：

1. 环境变量 `TYPORA_EXE`（显式指定，优先级最高）
2. 系统 PATH
3. Windows 注册表 App Paths（HKCU → HKLM，**跨用户最可靠**，任何安装位置都能找到）
4. 常见安装路径兜底

不同用户的 Typora 装在什么盘/目录都能被找到，无需手动告知路径。

## 注意事项

- 路径无后缀时自动补 `.md`；相对路径基于工作目录解析。
- read 返回内容超过 100000 字符时会截断并在结果中标注。
- 在 Typora 中打开文档后，Typora 的修改会自动写回磁盘，read 总能读到最新内容。
