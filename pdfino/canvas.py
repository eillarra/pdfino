"""Custom Canvas classes for PDFino."""

from reportlab.lib.pagesizes import mm
from reportlab.pdfgen.canvas import Canvas


class CanvasWithPageNumbers(Canvas):
    """A custom ReportLab canvas that adds page numbers to the bottom of each page."""

    def __init__(self, *args, **kwargs):
        """Initialize the canvas."""
        super().__init__(*args, **kwargs)

    def showPage(self):
        """Add a page number to the bottom of the page."""
        self.drawRightString(200 * mm, 20 * mm, f"Page {self._pageNumber}")
        super().showPage()
