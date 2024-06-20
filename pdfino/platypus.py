"""Custom layout classes for PDFino."""

import hashlib
import re
from typing import Any, Optional, TypedDict

from reportlab.lib.pagesizes import mm
from reportlab.pdfgen.canvas import Canvas as ReportLabCanvas
from reportlab.platypus import BaseDocTemplate as ReportLabDocTemplate
from reportlab.platypus import Flowable, Paragraph


class CanvasSignal(Flowable):
    """A flowable that it is only used to update custom_vars on Canvas."""

    def __init__(self, key: str, value: Any) -> None:
        self._custom_key = key
        self._custom_value = value
        super().__init__()

    def _drawOn(self, canv) -> None:
        canv.custom_vars[self._custom_key] = self._custom_value


class Canvas(ReportLabCanvas):
    """A custom ReportLab canvas that can receive signals."""

    custom_vars: TypedDict

    def __init__(self, *args, **kwargs):
        self.custom_vars = {}
        super().__init__(*args, **kwargs)

    def get_custom_var(self, key: str, default_value: Optional[Any] = None) -> Any:
        try:
            return self.custom_vars.get(key, default_value)
        except KeyError:
            return None

    @property
    def page_number(self) -> int:
        """The page number."""
        return self._pageNumber


class CanvasWithPageNumbers(Canvas):
    """A custom ReportLab canvas that adds page numbers to the bottom of each page."""

    def showPage(self):
        """Add a page number to the bottom of the page."""
        self.drawRightString(200 * mm, 20 * mm, f"Page {self.page_number}")
        super().showPage()


class DocTemplate(ReportLabDocTemplate):
    pass


class OutlineDocTemplate(DocTemplate):
    """A custom ReportLab document template that adds an outline."""

    def afterFlowable(self, flowable: Flowable):
        """Register outline entries. This assumes styles named as 'heading1', 'heading2', etc. or 'h1', 'h2', etc."""
        if isinstance(flowable, Paragraph):
            style = flowable.style.name.lower()

            if re.match(r"^(heading|h)\d$", style):
                level = int(style[-1]) - 1
                key = hashlib.shake_128(f"{level}-{flowable.getPlainText()}".encode()).hexdigest(4)
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(flowable.getPlainText(), key=key, level=level, closed=level > 2)
                self.notify("TOCEntry", (level, flowable.getPlainText(), self.page, key))
