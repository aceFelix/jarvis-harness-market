---
name: WPS Office
id: wps
description: 通过 COM 自动化控制 WPS Office 套件（文字/表格/演示）——打开、新建、编辑、保存、导出 PDF、表格读写、演示创建
when_to_use: 用户需要操作 WPS 文字、表格或演示文档时（打开、编辑、保存、导出、新建、批量写入）
trigger_words: [wps, 文档, 表格, 演示, office, 写字, 排版, et, kwps, kwpp]
command: jarvis-harness-wps
args:
  - name: subcommand
    type: string
    required: true
    positional: true
    enum: [writer, sheet, slide, status, version]
    description: "子命令：writer=文字操作, sheet=表格操作, slide=演示操作, status=检测环境, version=版本"
  - name: action
    type: string
    required: false
    description: "操作类型，各子命令不同（见命令树）"
  - name: target
    type: string
    required: false
    description: "文件路径 或 单元格地址（如 A1）"
  - name: text
    type: string
    required: false
    description: "文本内容 或 单元格值"
  - name: title
    type: string
    required: false
    description: "幻灯片标题（slide add_slide 用）"
  - name: data
    type: string
    required: false
    description: "批量写入数据（JSON 二维数组，sheet write_range 用）"
  - name: output_path
    type: string
    required: false
    description: "导出/保存路径"
  - name: mode
    type: string
    required: false
    enum: [append, insert, replace]
    description: "文本写入模式（writer edit_text 用，默认 append）"
  - name: layout
    type: string
    required: false
    enum: [text, blank]
    description: "幻灯片版式（slide add_slide 用，默认 text）"
  - name: sheet_name
    type: string
    required: false
    description: "工作表名（sheet 操作用，默认活动工作表）"
  - name: headless
    type: boolean
    required: false
    description: "是否不显示 WPS 窗口（后台操作，默认 false）"
  - name: json
    type: boolean
    required: false
    default: true
    description: "是否添加 --json 标志输出结构化 JSON（推荐开启）"
examples:
  - "jarvis-harness-wps status"
  - "jarvis-harness-wps writer --action open_doc --target C:\\Users\\me\\报告.docx"
  - "jarvis-harness-wps sheet --action write_cell --target A1 --text 姓名"
  - "jarvis-harness-wps writer --action export_pdf --output-path C:\\Users\\me\\报告.pdf"
  - "jarvis-harness-wps slide --action add_slide --title 项目汇报 --text 第一页正文"
---

# WPS Office Harness

通过 COM 自动化（win32com）控制 WPS Office 套件，支持 WPS 文字、表格、演示三大组件。

## 安装

```bash
pip install jarvis-harness-wps
```

## 命令树

```
jarvis-harness-wps writer --action <action> [options]
  ├── open_doc     打开文档         --target <文件路径>
  ├── new_doc      新建空白文字文档
  ├── edit_text    编辑文本         --text <内容> --mode [append|insert|replace]
  ├── save         保存文档         --output-path <路径>
  ├── export_pdf   导出为 PDF       --output-path <路径>
  ├── close        关闭文档         --no-save
  └── info         获取文档信息

jarvis-harness-wps sheet --action <action> [options]
  ├── open_sheet       打开表格      --target <文件路径>
  ├── new_sheet        新建工作簿
  ├── write_cell        写入单元格   --target <地址> --text <值>
  ├── read_cell         读取单元格   --target <地址>
  ├── write_range       批量写入     --target <起始单元格> --data '[[...],[...]]'
  ├── save             保存工作簿    --output-path <路径>
  └── export_pdf       导出为 PDF   --output-path <路径>

jarvis-harness-wps slide --action <action> [options]
  ├── open_presentation    打开演示   --target <文件路径>
  ├── new_presentation     新建演示
  ├── add_slide           添加幻灯片  --title <标题> --text <正文> --layout [text|blank]
  ├── save               保存演示    --output-path <路径>
  ├── export_pdf         导出为 PDF  --output-path <路径>
  └── info               获取演示信息

jarvis-harness-wps status          检测 WPS 进程与环境
jarvis-harness-wps version         显示 harness 版本
```

## 前置条件

- **Windows 系统**（COM 自动化仅限 Windows）
- **已安装 WPS Office**（或 Microsoft Office 作为回退）
- **已安装 pywin32**：`pip install pywin32`

## COM ProgID

| 组件 | WPS ProgID | MS Office 回退 |
|------|-----------|----------------|
| 文字 (Writer) | Kwps.Application | Word.Application |
| 表格 (Spreadsheet) | Ket.Application | Excel.Application |
| 演示 (Presentation) | Kwpp.Application | PowerPoint.Application |

## 注意事项

- COM 操作需要 WPS 进程可被 COM 调用（默认支持）
- 导出 PDF 需指定绝对路径
- 批量写入的 data 参数必须是 JSON 二维数组
- 操作完成后文档保持打开状态（除非调用 close）
- headless 参数可让 WPS 窗口不显示（后台操作）
