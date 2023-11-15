"""PDFino is a thin wrapper around ReportLab to make it easier to create PDFs."""

from reportlab.rl_config import canvas_basefontname as default_font_name

from .main import Document, Template
from .type_definitions import Font, Margins, Pagesize, Style


__version__ = "0.1.0"
__all__ = [
    "Template",
    "Document",
    "Font",
    "Margins",
    "Style",
    "Pagesize",
    "default_font_name",
]
