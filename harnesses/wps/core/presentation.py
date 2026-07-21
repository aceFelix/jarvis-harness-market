"""WPS 演示 (Presentation) — 新建演示文稿、添加幻灯片、插入文本。

通过 COM 接口（Kwpp.Application / PowerPoint.Application）操作 WPS 演示。

@author aceFelix
"""

from __future__ import annotations

from typing import Any

from utils.wps_backend import (
    get_presentation_app,
    resolve_path,
    WPSBackendError,
)

# PowerPoint/WPS 常量
PpSaveAsPresentation = 1   # .ppt
PpSaveAsOpenXMLPresentation = 24  # .pptx
PpSaveAsPDF = 32             # PDF
PpLayoutBlank = 12           # 空白版式
PpLayoutText = 1             # 标题+正文


def new_presentation(*, visible: bool = True) -> dict[str, Any]:
    """新建空白 WPS 演示文稿。

    Returns:
        包含 status、slide_count 的字典
    """
    try:
        app = get_presentation_app(visible=visible)
        pres = app.Presentations.Add()
        return {
            "status": "ok",
            "action": "new_presentation",
            "slide_count": pres.Slides.Count,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"新建演示失败: {e}"}


def open_presentation(file_path: str, *, workdir: str = "", visible: bool = True) -> dict[str, Any]:
    """打开已有的 WPS 演示文件。"""
    import os
    full_path = resolve_path(file_path, workdir)

    if not os.path.isfile(full_path):
        return {"status": "error", "message": f"文件不存在: {full_path}"}

    try:
        app = get_presentation_app(visible=visible)
        pres = app.Presentations.Open(full_path)
        return {
            "status": "ok",
            "action": "open_presentation",
            "file_path": full_path,
            "slide_count": pres.Slides.Count,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"打开演示失败: {e}"}


def add_slide(title: str = "", body: str = "", *, layout: str = "text") -> dict[str, Any]:
    """添加一张幻灯片。

    Args:
        title: 标题文本
        body: 正文文本
        layout: 版式类型 "text"(标题+正文) 或 "blank"(空白)

    Returns:
        包含 status、slide_index 的字典
    """
    try:
        app = get_presentation_app(visible=True)
        pres = app.ActivePresentation
        if pres is None:
            return {"status": "error", "message": "没有活动演示文稿"}

        layout_id = PpLayoutText if layout == "text" else PpLayoutBlank
        slide_count = pres.Slides.Count
        slide = pres.Slides.Add(slide_count + 1, layout_id)

        # 填充文本
        if title and layout == "text":
            # shape[0] = 标题占位符
            try:
                slide.Shapes.Placeholders(1).TextFrame.TextRange.Text = title
            except Exception:
                pass
        if body and layout == "text":
            try:
                slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = body
            except Exception:
                pass

        return {
            "status": "ok",
            "action": "add_slide",
            "slide_index": slide.SlideIndex,
            "title": title,
            "body": body,
            "layout": layout,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"添加幻灯片失败: {e}"}


def save_presentation(*, file_path: str = "", workdir: str = "") -> dict[str, Any]:
    """保存当前演示文稿。"""
    try:
        app = get_presentation_app(visible=True)
        pres = app.ActivePresentation
        if pres is None:
            return {"status": "error", "message": "没有活动演示文稿"}

        if file_path:
            full_path = resolve_path(file_path, workdir)
            ext = full_path.lower().rsplit(".", 1)[-1] if "." in full_path else "pptx"
            fmt_map = {
                "ppt": PpSaveAsPresentation,
                "pptx": PpSaveAsOpenXMLPresentation,
                "pdf": PpSaveAsPDF,
            }
            file_format = fmt_map.get(ext, PpSaveAsOpenXMLPresentation)
            pres.SaveAs(full_path, file_format)
            saved_path = full_path
        else:
            pres.Save()
            saved_path = pres.FullName

        return {
            "status": "ok",
            "action": "save",
            "file_path": saved_path,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"保存演示失败: {e}"}


def export_pdf(output_path: str, *, workdir: str = "") -> dict[str, Any]:
    """将当前演示文稿导出为 PDF。"""
    full_path = resolve_path(output_path, workdir)
    if not full_path.lower().endswith(".pdf"):
        full_path += ".pdf"

    try:
        app = get_presentation_app(visible=True)
        pres = app.ActivePresentation
        if pres is None:
            return {"status": "error", "message": "没有活动演示文稿"}

        pres.SaveAs(full_path, PpSaveAsPDF)
        return {
            "status": "ok",
            "action": "export_pdf",
            "output_path": full_path,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"导出 PDF 失败: {e}"}


def get_presentation_info() -> dict[str, Any]:
    """获取当前演示文稿信息。"""
    try:
        app = get_presentation_app(visible=True)
        pres = app.ActivePresentation
        if pres is None:
            return {"status": "ok", "active_presentation": False}

        return {
            "status": "ok",
            "active_presentation": True,
            "name": pres.Name,
            "full_path": pres.FullName,
            "slide_count": pres.Slides.Count,
        }
    except WPSBackendError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"获取演示信息失败: {e}"}
