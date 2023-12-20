"""Custom layout classes for PDFino."""

import hashlib
import re

from reportlab.lib.pagesizes import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import BaseDocTemplate, Flowable, Paragraph


class CanvasWithPageNumbers(Canvas):
    """A custom ReportLab canvas that adds page numbers to the bottom of each page."""

    def showPage(self):
        """Add a page number to the bottom of the page."""
        self.drawRightString(200 * mm, 20 * mm, f"Page {self._pageNumber}")
        super().showPage()


class OutlineDocTemplate(BaseDocTemplate):
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
