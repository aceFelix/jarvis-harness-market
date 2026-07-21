"""WPS 表格 (Spreadsheet) — 新建工作簿、读写单元格、批量写入。

通过 COM 接口（Ket.Application / Excel.Application）操作 WPS 表格。

@author aceFelix
"""

from __future__ import annotations

from typing import Any

from jarvis_harness_wps.utils.wps_backend import (
    get_spreadsheet_app,
    resolve_path,
    WPSBackendError,
)

# Excel/WPS 常量
XlFileFormat_xlsx = 51     # .xlsx
XlFileFormat_xls = 56      # .xls
XlFileFormat_csv = 6       # .csv
XlFileFormat_pdf = 57      # PDF (xlTypePDF)


def new_workbook(*, visible: bool = True) -> dict[str, Any]:
    """新建空白 WPS 表格工作簿。

    Returns:
        包含 status、sheet_name 的字典
    """
    try:
        app = get_spreadsheet_app(visible=visible)
        wb = app.Workbooks.Add()
        sheet = wb.ActiveSheet
        return {
            "status": "ok",
            "action": "new_sheet",
            "sheet_name": sheet.Name,
            "sheet_count": wb.Sheets.Count,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"新建工作簿失败: {e}"}


def open_workbook(file_path: str, *, workdir: str = "", visible: bool = True) -> dict[str, Any]:
    """打开已有的 WPS 表格文件。

    Args:
        file_path: 文件路径
        workdir: 工作目录
        visible: 是否显示窗口

    Returns:
        包含 status、file_path、sheet_name 的字典
    """
    import os
    full_path = resolve_path(file_path, workdir)

    if not os.path.isfile(full_path):
        return {"status": "error", "message": f"文件不存在: {full_path}"}

    try:
        app = get_spreadsheet_app(visible=visible)
        wb = app.Workbooks.Open(full_path)
        sheet = wb.ActiveSheet
        return {
            "status": "ok",
            "action": "open_sheet",
            "file_path": full_path,
            "sheet_name": sheet.Name,
            "sheet_count": wb.Sheets.Count,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"打开表格失败: {e}"}


def write_cell(cell: str, value: str, *, sheet_name: str = "") -> dict[str, Any]:
    """向指定单元格写入数据。

    Args:
        cell: 单元格地址（如 "A1", "B2", "C3"）
        value: 要写入的值
        sheet_name: 工作表名（为空则使用活动工作表）

    Returns:
        包含 status、cell、value 的字典
    """
    if not cell:
        return {"status": "error", "message": "cell 参数不能为空"}

    try:
        app = get_spreadsheet_app(visible=True)
        wb = app.ActiveWorkbook
        if wb is None:
            return {"status": "error", "message": "没有活动工作簿，请先打开或新建表格"}

        sheet = wb.Sheets(sheet_name) if sheet_name else wb.ActiveSheet
        sheet.Range(cell).Value = value
        return {
            "status": "ok",
            "action": "write_cell",
            "sheet": sheet.Name,
            "cell": cell,
            "value": str(value),
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"写入单元格失败: {e}"}


def read_cell(cell: str, *, sheet_name: str = "") -> dict[str, Any]:
    """读取指定单元格内容。

    Args:
        cell: 单元格地址
        sheet_name: 工作表名

    Returns:
        包含 status、cell、value 的字典
    """
    if not cell:
        return {"status": "error", "message": "cell 参数不能为空"}

    try:
        app = get_spreadsheet_app(visible=True)
        wb = app.ActiveWorkbook
        if wb is None:
            return {"status": "error", "message": "没有活动工作簿"}

        sheet = wb.Sheets(sheet_name) if sheet_name else wb.ActiveSheet
        value = sheet.Range(cell).Value
        return {
            "status": "ok",
            "action": "read_cell",
            "sheet": sheet.Name,
            "cell": cell,
            "value": str(value) if value is not None else "",
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"读取单元格失败: {e}"}


def write_range(start_cell: str, data: list[list[Any]], *, sheet_name: str = "") -> dict[str, Any]:
    """批量写入数据（从起始单元格开始）。

    Args:
        start_cell: 起始单元格（如 "A1"）
        data: 二维列表，每行为一个子列表
        sheet_name: 工作表名

    Returns:
        包含 status、rows、cols 的字典
    """
    if not start_cell or not data:
        return {"status": "error", "message": "start_cell 和 data 参数不能为空"}

    try:
        app = get_spreadsheet_app(visible=True)
        wb = app.ActiveWorkbook
        if wb is None:
            return {"status": "error", "message": "没有活动工作簿"}

        sheet = wb.Sheets(sheet_name) if sheet_name else wb.ActiveSheet

        rows = len(data)
        cols = max(len(row) for row in data)

        # 计算目标范围
        start_range = sheet.Range(start_cell)
        # 将二维列表展平为一维，COM 需要 SafeArray
        flat_data = []
        for row in data:
            # 补齐每行到最大列数
            padded = list(row) + [""] * (cols - len(row))
            flat_data.append(padded)

        end_cell = _offset_cell(start_cell, rows - 1, cols - 1)
        target_range = sheet.Range(f"{start_cell}:{end_cell}")
        target_range.Value = flat_data

        return {
            "status": "ok",
            "action": "write_range",
            "sheet": sheet.Name,
            "start_cell": start_cell,
            "end_cell": end_cell,
            "rows": rows,
            "cols": cols,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"批量写入失败: {e}"}


def save_workbook(*, file_path: str = "", workdir: str = "") -> dict[str, Any]:
    """保存当前工作簿。

    Args:
        file_path: 另存为路径（为空则保存到原路径）
        workdir: 工作目录

    Returns:
        包含 status、file_path 的字典
    """
    try:
        app = get_spreadsheet_app(visible=True)
        wb = app.ActiveWorkbook
        if wb is None:
            return {"status": "error", "message": "没有活动工作簿"}

        if file_path:
            full_path = resolve_path(file_path, workdir)
            ext = full_path.lower().rsplit(".", 1)[-1] if "." in full_path else "xlsx"
            fmt_map = {
                "xlsx": XlFileFormat_xlsx,
                "xls": XlFileFormat_xls,
                "csv": XlFileFormat_csv,
                "pdf": XlFileFormat_pdf,
            }
            file_format = fmt_map.get(ext, XlFileFormat_xlsx)
            wb.SaveAs(full_path, FileFormat=file_format)
            saved_path = full_path
        else:
            wb.Save()
            saved_path = wb.FullName

        return {
            "status": "ok",
            "action": "save",
            "file_path": saved_path,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"保存工作簿失败: {e}"}


def export_pdf(output_path: str, *, workdir: str = "") -> dict[str, Any]:
    """将当前工作簿导出为 PDF。"""
    full_path = resolve_path(output_path, workdir)
    if not full_path.lower().endswith(".pdf"):
        full_path += ".pdf"

    try:
        app = get_spreadsheet_app(visible=True)
        wb = app.ActiveWorkbook
        if wb is None:
            return {"status": "error", "message": "没有活动工作簿"}

        # ExportAsFixedFormat: Type=0=xlTypePDF
        wb.ExportAsFixedFormat(Type=0, FileName=full_path, OpenAfterPublish=False)
        return {
            "status": "ok",
            "action": "export_pdf",
            "output_path": full_path,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"导出 PDF 失败: {e}"}


# ── 辅助函数 ──────────────────────────────────────────────────────────

def _offset_cell(cell: str, row_offset: int, col_offset: int) -> str:
    """计算从起始单元格偏移后的单元格地址。

    Args:
        cell: 起始单元格（如 "A1"）
        row_offset: 行偏移
        col_offset: 列偏移

    Returns:
        偏移后的单元格地址（如 "B3"）
    """
    # 解析列字母和行号
    col_str = ""
    row_str = ""
    for ch in cell:
        if ch.isalpha():
            col_str += ch
        else:
            row_str += ch

    col_str = col_str.upper()
    row_num = int(row_str) if row_str else 1

    # 列号转数字
    col_num = 0
    for ch in col_str:
        col_num = col_num * 26 + (ord(ch) - ord("A") + 1)

    # 偏移
    col_num += col_offset
    row_num += row_offset

    # 数字转列号
    col_letters = ""
    while col_num > 0:
        col_num -= 1
        col_letters = chr(ord("A") + (col_num % 26)) + col_letters
        col_num //= 26

    return f"{col_letters}{row_num}"
