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
