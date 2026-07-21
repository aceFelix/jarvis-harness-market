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
    description: "要执行的子命令。格式: <component> --action <action> [options]。component 为 writer/sheet/slide/status/version。参考下方命令树。"
  - name: json
    type: boolean
    required: false
    default: true
    description: "是否添加 --json 标志输出结构化 JSON（推荐开启）。"
examples:
  - "jarvis-harness-wps --json writer --action open_doc --target C:\\Users\\me\\报告.docx"
  - "jarvis-harness-wps --json sheet --action new_sheet"
  - "jarvis-harness-wps --json sheet --action write_cell --target A1 --text 姓名"
  - "jarvis-harness-wps --json writer --action export_pdf --output-path C:\\Users\\me\\报告.pdf"
  - "jarvis-harness-wps --json slide --action add_slide --title 项目汇报 --text 第一页正文"
  - "jarvis-harness-wps --json status"
---

# WPS Office Harness

通过 COM 自动化（win32com）控制 WPS Office 套件，支持 WPS 文字、表格、演示三大组件。

## 安装

```bash
pip install jarvis-harness-wps
# 或从 GitHub 安装：
pip install git+https://github.com/<user>/jarvis-harness-market.git#subdirectory=harnesses/wps
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

## 操作详情

### Writer（WPS 文字）

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| open_doc | 打开已有文档 | target(文件路径) | headless |
| new_doc | 新建空白文档 | 无 | headless |
| edit_text | 插入/替换文本 | text | mode(append/insert/replace) |
| save | 保存或另存为 | 无 | output_path |
| export_pdf | 导出为 PDF | output_path | 无 |
| close | 关闭当前文档 | 无 | no_save |
| info | 获取文档信息 | 无 | 无 |

### Sheet（WPS 表格）

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| open_sheet | 打开已有表格 | target(文件路径) | headless |
| new_sheet | 新建空白工作簿 | 无 | headless |
| write_cell | 写入单元格 | target(地址), text | sheet_name |
| read_cell | 读取单元格 | target(地址) | sheet_name |
| write_range | 批量写入 | target(起始单元格), data(JSON) | sheet_name |
| save | 保存或另存为 | 无 | output_path |
| export_pdf | 导出为 PDF | output_path | 无 |

### Slide（WPS 演示）

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| open_presentation | 打开已有演示 | target(文件路径) | headless |
| new_presentation | 新建空白演示 | 无 | headless |
| add_slide | 添加幻灯片 | 无 | title, text, layout |
| save | 保存或另存为 | 无 | output_path |
| export_pdf | 导出为 PDF | output_path | 无 |
| info | 获取演示信息 | 无 | 无 |

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
- --headless 参数可让 WPS 窗口不显示（后台操作）
---
name: WPS Office
id: wps
description: 通过 COM 自动化控制 WPS Office 套件（文字/表格/演示）——打开、新建、编辑、保存、导出 PDF、表格读写、演示创建
when_to_use: 用户需要操作 WPS 文字、表格或演示文档时（打开、编辑、保存、导出、新建、批量写入）
trigger_words: [wps, 文档, 表格, 演示, office, 写字, 排版, et, kwps, kwpp]
command: python
args:
  - name: command
    type: string
    required: true
    enum: [writer, sheet, slide, status, version]
    description: "子命令：writer=文字操作, sheet=表格操作, slide=演示操作, status=检测环境, version=版本"
  - name: action
    type: string
    required: true
    description: "操作类型，各子命令不同（见下表）"
  - name: target
    type: string
    required: false
    description: "文件路径 或 单元格地址"
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
examples:
  - "用 WPS 打开桌面上的报告.docx"
  - "新建一个 WPS 表格，在 A1 写入姓名，B1 写入年龄"
  - "把当前 WPS 文档导出为 PDF"
  - "读取 WPS 表格中 C3 单元格的内容"
  - "新建 WPS 演示文稿，添加一张标题为'项目汇报'的幻灯片"
  - "批量写入表格数据到 A1:C5"
  - "检测 WPS 是否在运行"
---

# WPS Office Harness

通过 COM 自动化（win32com）控制 WPS Office 套件，支持 WPS 文字、表格、演示三大组件。

## 命令树

```
wps writer --action <action> [options]
  ├── open_doc     打开文档         --target <文件路径>
  ├── new_doc      新建空白文字文档
  ├── edit_text    编辑文本         --text <内容> --mode [append|insert|replace]
  ├── save         保存文档         --output-path <路径>
  ├── export_pdf   导出为 PDF       --output-path <路径>
  ├── close        关闭文档         --no-save
  └── info         获取文档信息

wps sheet --action <action> [options]
  ├── open_sheet       打开表格      --target <文件路径>
  ├── new_sheet        新建工作簿
  ├── write_cell        写入单元格   --target <地址> --text <值>
  ├── read_cell         读取单元格   --target <地址>
  ├── write_range       批量写入     --target <起始单元格> --data '[[...],[...]]'
  ├── save             保存工作簿    --output-path <路径>
  └── export_pdf       导出为 PDF   --output-path <路径>

wps slide --action <action> [options]
  ├── open_presentation    打开演示   --target <文件路径>
  ├── new_presentation     新建演示
  ├── add_slide           添加幻灯片  --title <标题> --text <正文> --layout [text|blank]
  ├── save               保存演示    --output-path <路径>
  ├── export_pdf         导出为 PDF  --output-path <路径>
  └── info               获取演示信息

wps status          检测 WPS 进程与环境
wps version         显示 harness 版本
```

## 操作详情

### Writer（WPS 文字）

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| open_doc | 打开已有文档 | target(文件路径) | headless |
| new_doc | 新建空白文档 | 无 | headless |
| edit_text | 插入/替换文本 | text | mode(append/insert/replace) |
| save | 保存或另存为 | 无 | output_path |
| export_pdf | 导出为 PDF | output_path | 无 |
| close | 关闭当前文档 | 无 | no_save |
| info | 获取文档信息（名称、路径、字数、页数） | 无 | 无 |

### Sheet（WPS 表格）

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| open_sheet | 打开已有表格 | target(文件路径) | headless |
| new_sheet | 新建空白工作簿 | 无 | headless |
| write_cell | 写入单元格 | target(地址), text | sheet_name |
| read_cell | 读取单元格 | target(地址) | sheet_name |
| write_range | 批量写入 | target(起始单元格), data(JSON) | sheet_name |
| save | 保存或另存为 | 无 | output_path |
| export_pdf | 导出为 PDF | output_path | 无 |

### Slide（WPS 演示）

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| open_presentation | 打开已有演示 | target(文件路径) | headless |
| new_presentation | 新建空白演示 | 无 | headless |
| add_slide | 添加幻灯片 | 无 | title, text, layout |
| save | 保存或另存为 | 无 | output_path |
| export_pdf | 导出为 PDF | output_path | 无 |
| info | 获取演示信息 | 无 | 无 |

## 前置条件

- **Windows 系统**（COM 自动化仅限 Windows）
- **已安装 WPS Office**（或 Microsoft Office 作为回退）
- **已安装 pywin32**：`pip install pywin32`

## 使用方式

```bash
# 检测环境
python run.py status

# 打开文档
python run.py writer --action open_doc --target "C:\Users\me\报告.docx"

# 新建表格，写入 A1
python run.py sheet --action new_sheet
python run.py sheet --action write_cell --target A1 --text "姓名"

# 批量写入 A1:C3
python run.py sheet --action write_range --target A1 --data '[["姓名","年龄","城市"],["张三","25","北京"],["李四","30","上海"]]'

# 导出 PDF
python run.py writer --action export_pdf --output-path "C:\Users\me\报告.pdf"

# 新建演示，添加幻灯片
python run.py slide --action new_presentation
python run.py slide --action add_slide --title "项目汇报" --text "第一页正文内容"
```

## 架构设计

```
harnesses/wps/
├── __init__.py              ← 包入口 + 版本
├── __main__.py              ← python -m wps 入口
├── run.py                   ← CLI 入口（argparse 子命令树）
├── SKILL.md                 ← Agent 技能定义（本文件）
├── core/
│   ├── __init__.py
│   ├── writer.py            ← WPS 文字 COM 操作
│   ├── spreadsheet.py       ← WPS 表格 COM 操作
│   └── presentation.py     ← WPS 演示 COM 操作
└── utils/
    ├── __init__.py
    └── wps_backend.py       ← COM 后端管理（连接、进程检测、路径工具）
```

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
---
name: WPS Office
id: wps
description: 通过 COM 自动化控制 WPS Office（打开文档、编辑文本、保存、导出 PDF、新建表格）
when_to_use: 用户需要操作 WPS 文字、表格或演示文档时（打开、编辑、保存、导出、新建）
trigger_words: [wps, 文档, 表格, 演示, office, 写字, 排版]
command: python
args:
  - name: action
    type: string
    required: true
    enum: [open_doc, new_doc, edit_text, save, export_pdf, new_sheet, write_cell, read_cell, new_presentation]
    description: "操作类型：open_doc=打开文档, new_doc=新建文字文档, edit_text=编辑文本, save=保存, export_pdf=导出PDF, new_sheet=新建表格, write_cell=写入单元格, read_cell=读取单元格, new_presentation=新建演示"
  - name: target
    type: string
    required: false
    description: "操作对象（文件路径 或 单元格地址如 A1）"
  - name: text
    type: string
    required: false
    description: "要写入的文本内容"
  - name: output_path
    type: string
    required: false
    description: "导出/保存路径（action=export_pdf 时必填）"
examples:
  - "用 WPS 打开桌面上的报告.docx"
  - "新建一个 WPS 表格，在 A1 写入姓名，B1 写入年龄"
  - "把当前 WPS 文档导出为 PDF"
  - "读取 WPS 表格中 C3 单元格的内容"
---

# WPS Office Harness

通过 COM 自动化（win32com）控制 WPS Office 套件。

## 支持的操作

| action | 说明 | 必填参数 |
|--------|------|----------|
| open_doc | 打开指定文档 | target(文件路径) |
| new_doc | 新建空白文字文档 | 无 |
| edit_text | 在文档光标处插入/替换文本 | text |
| save | 保存当前文档 | 无 |
| export_pdf | 导出当前文档为 PDF | output_path |
| new_sheet | 新建空白表格 | 无 |
| write_cell | 向指定单元格写入数据 | target(单元格), text |
| read_cell | 读取指定单元格内容 | target(单元格) |
| new_presentation | 新建空白演示 | 无 |

## 前置条件

- Windows 系统
- 已安装 WPS Office
- 已安装 `pywin32`（pip install pywin32）

## 使用方式

```bash
python run.py --action open_doc --target "C:\Users\me\报告.docx" --harness-dir <dir> --workdir <dir>
```

## 注意事项

- COM 自动化需要 WPS 进程可被 COM 调用（通常默认支持）
- 操作完成后文档保持打开状态，需手动或调用 close 关闭
- 导出 PDF 需要指定绝对路径
