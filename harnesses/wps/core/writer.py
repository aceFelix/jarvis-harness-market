"""WPS 文字 (Writer) — 文档打开、新建、编辑、保存、导出 PDF。

通过 COM 接口（Kwps.Application / Word.Application）操作 WPS 文字文档。

@author aceFelix
"""

from __future__ import annotations

from typing import Any

from utils.wps_backend import (
    get_writer_app,
    resolve_path,
    WPSBackendError,
)

# Word/WPS 常量
WdFormatDocument = 0        # .doc
WdFormatDocumentDefault = 16  # .docx
WdFormatPDF = 17            # PDF
WdDoNotSaveChanges = 0
WdSaveChanges = -1


def open_document(file_path: str, *, workdir: str = "", visible: bool = True) -> dict[str, Any]:
    """打开已有的 WPS 文字文档。

    Args:
        file_path: 文件路径（支持相对路径）
        workdir: 工作目录
        visible: 是否显示窗口

    Returns:
        包含 status、file_path、doc_name 的字典
    """
    full_path = resolve_path(file_path, workdir)

    import os
    if not os.path.isfile(full_path):
        return {"status": "error", "message": f"文件不存在: {full_path}"}

    try:
        app = get_writer_app(visible=visible)
        doc = app.Documents.Open(full_path)
        return {
            "status": "ok",
            "action": "open_doc",
            "file_path": full_path,
            "doc_name": doc.Name,
            "doc_count": app.Documents.Count,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"打开文档失败: {e}"}


def new_document(*, visible: bool = True) -> dict[str, Any]:
    """新建空白 WPS 文字文档。

    Returns:
        包含 status、doc_name 的字典
    """
    try:
        app = get_writer_app(visible=visible)
        doc = app.Documents.Add()
        return {
            "status": "ok",
            "action": "new_doc",
            "doc_name": doc.Name,
            "doc_count": app.Documents.Count,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"新建文档失败: {e}"}


def edit_text(text: str, *, mode: str = "append") -> dict[str, Any]:
    """向当前文档插入/替换文本。

    Args:
        text: 要写入的文本内容
        mode: 写入模式 append=追加到末尾, insert=光标处插入, replace=全选替换

    Returns:
        包含 status、written_text 的字典
    """
    if not text:
        return {"status": "error", "message": "text 参数不能为空"}

    try:
        app = get_writer_app(visible=True)
        doc = app.ActiveDocument
        if doc is None:
            return {"status": "error", "message": "没有活动文档，请先打开或新建文档"}

        if mode == "replace":
            # 全选替换
            sel = app.Selection
            sel.WholeStory()
            sel.TypeText(text)
        elif mode == "insert":
            # 光标处插入
            app.Selection.TypeText(text)
        else:
            # 追加到文档末尾
            content = doc.Content
            content.Collapse(0)  # 0=wdCollapseEnd
            content.InsertAfter(text)

        return {
            "status": "ok",
            "action": "edit_text",
            "mode": mode,
            "written_text": text,
            "doc_name": doc.Name,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"写入文本失败: {e}"}


def save_document(*, file_path: str = "", workdir: str = "") -> dict[str, Any]:
    """保存当前文档。

    Args:
        file_path: 另存为路径（为空则保存到原路径）
        workdir: 工作目录

    Returns:
        包含 status、file_path 的字典
    """
    try:
        app = get_writer_app(visible=True)
        doc = app.ActiveDocument
        if doc is None:
            return {"status": "error", "message": "没有活动文档"}

        if file_path:
            full_path = resolve_path(file_path, workdir)
            # 根据扩展名决定格式
            ext = full_path.lower().rsplit(".", 1)[-1] if "." in full_path else "docx"
            fmt_map = {
                "doc": WdFormatDocument,
                "docx": WdFormatDocumentDefault,
                "pdf": WdFormatPDF,
            }
            file_format = fmt_map.get(ext, WdFormatDocumentDefault)
            doc.SaveAs2(full_path, FileFormat=file_format)
            saved_path = full_path
        else:
            doc.Save()
            saved_path = doc.FullName

        return {
            "status": "ok",
            "action": "save",
            "file_path": saved_path,
            "doc_name": doc.Name,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"保存文档失败: {e}"}


def export_pdf(output_path: str, *, workdir: str = "") -> dict[str, Any]:
    """将当前文档导出为 PDF。

    Args:
        output_path: PDF 输出路径
        workdir: 工作目录

    Returns:
        包含 status、output_path 的字典
    """
    full_path = resolve_path(output_path, workdir)

    # 确保 .pdf 扩展名
    if not full_path.lower().endswith(".pdf"):
        full_path += ".pdf"

    try:
        app = get_writer_app(visible=True)
        doc = app.ActiveDocument
        if doc is None:
            return {"status": "error", "message": "没有活动文档"}

        doc.ExportAsFixedFormat(
            OutputFileName=full_path,
            ExportFormat=WdFormatPDF,
            OpenAfterExport=False,
        )
        return {
            "status": "ok",
            "action": "export_pdf",
            "output_path": full_path,
            "doc_name": doc.Name,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"导出 PDF 失败: {e}"}


def close_document(*, save: bool = True) -> dict[str, Any]:
    """关闭当前文档。

    Args:
        save: 是否在关闭前保存

    Returns:
        包含 status 的字典
    """
    try:
        app = get_writer_app(visible=True)
        doc = app.ActiveDocument
        if doc is None:
            return {"status": "ok", "action": "close", "message": "没有活动文档"}

        doc_name = doc.Name
        save_flag = WdSaveChanges if save else WdDoNotSaveChanges
        doc.Close(SaveChanges=save_flag)
        return {
            "status": "ok",
            "action": "close",
            "doc_name": doc_name,
            "saved": save,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"关闭文档失败: {e}"}


def get_document_info() -> dict[str, Any]:
    """获取当前文档信息（名称、路径、字数、段落数）。"""
    try:
        app = get_writer_app(visible=True)
        doc = app.ActiveDocument
        if doc is None:
            return {"status": "ok", "active_document": False}

        return {
            "status": "ok",
            "active_document": True,
            "doc_name": doc.Name,
            "full_path": doc.FullName,
            "word_count": doc.Words.Count,
            "paragraph_count": doc.Paragraphs.Count,
            "page_count": doc.ComputeStatistics(2),  # 2=wdStatisticPages
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"获取文档信息失败: {e}"}
