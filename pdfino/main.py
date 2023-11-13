"""Module for the main PDFINO classes and API."""

import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.fonts import tt2ps
from reportlab.lib.pagesizes import A4, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import BaseDocTemplate, Flowable, PageBreak, PageTemplate, Paragraph, Spacer
from reportlab.platypus.frames import Frame
from reportlab.rl_config import canvas_basefontname

from .styles import ParagraphStyle, Stylesheet, get_sample_stylesheet
from .type_definitions import ElementOptions, Font, Margins, Style
from .utils import get_margins


REPORTLAB_INNER_FRAME_PADDING = 6


class Template:
    """A template that can be used to generate a PDF file."""

    pagesize: Tuple[int, int] = A4
    margins: Margins = Margins(15 * mm, 15 * mm, 15 * mm, 15 * mm)
    fonts: List[Font] = []
    use_sample_stylesheet: bool = True
    styles: List[Union[Style, ParagraphStyle]] = []

    def __init__(self) -> None:
        """Initialize the template."""
        self._register_fonts()
        self._setup_styles()

    def _register_fonts(self) -> None:
        for font in self.fonts:
            if not font.normal or not font.normal.is_file():
                raise ValueError(f"Font {font.name} must have a normal variant which is an existing file.")

            registerFont(TTFont(font.name, font.normal))

            variants = [
                ("-Bold", font.bold),
                ("-Italic", font.italic),
                ("-BoldItalic", font.bold_italic),
            ]

            for suffix, variant in variants:
                if variant:
                    assert variant.is_file(), f"Font file {variant} ({suffix}) does not exist."
                    registerFont(TTFont(f"{font.name}{suffix}", variant))

            registerFontFamily(
                font.name,
                normal=font.name,
                bold=f"{font.name}-Bold" if font.bold else None,
                italic=f"{font.name}-Italic" if font.italic else None,
                boldItalic=f"{font.name}-BoldItalic" if font.bold_italic else None,
            )

    def _replace_default_fonts(self) -> None:
        if not self.default_font:
            return

        replace_map = {
            canvas_basefontname: self.default_font.name,
            tt2ps(canvas_basefontname, 1, 0): tt2ps(self.default_font.name, 1, 0),
            tt2ps(canvas_basefontname, 0, 1): tt2ps(self.default_font.name, 0, 1),
            tt2ps(canvas_basefontname, 1, 1): tt2ps(self.default_font.name, 1, 1),
        }

        for style in self._stylesheet.byName.values():
            try:
                if style.fontName in replace_map:
                    style.fontName = replace_map[style.fontName]
            except AttributeError:
                pass

    def _setup_styles(self) -> None:
        if self.use_sample_stylesheet:
            self._stylesheet = get_sample_stylesheet()
            self._stylesheet.add(ParagraphStyle("p", parent=self._stylesheet["Normal"]))
            self._replace_default_fonts()
        else:
            self._stylesheet = Stylesheet()

        for style in self.styles:
            if isinstance(style, Style):
                assert (
                    style.font_name in pdfmetrics.getRegisteredFontNames()
                ), f"Font {style.font_name} is not registered."
                paragraph_style = self._style_to_reportlab(style)
            elif isinstance(style, ParagraphStyle):
                paragraph_style = style

            try:
                self._stylesheet.add(paragraph_style)
            except KeyError:
                self._stylesheet[style.name].__dict__.update(paragraph_style.__dict__)

    @staticmethod
    def _style_to_reportlab(style: Style) -> ParagraphStyle:
        return ParagraphStyle(
            style.name,
            fontName=style.font_name,
            fontSize=style.font_size,
            textColor=HexColor(style.color),
        )

    @property
    def default_font(self) -> Optional[Font]:
        """Return the default font."""
        return next((font for font in self.fonts if font.default), None)


class Document:
    """A PDF document."""

    template_class = Template

    def __init__(self) -> None:
        """Initialize the document."""
        self.buffer = io.BytesIO()
        self.template = self.template_class()
        self.doc = BaseDocTemplate(
            self.buffer,
            pagesize=self.template_class.pagesize,
            topMargin=self.template_class.margins.top - REPORTLAB_INNER_FRAME_PADDING,  # compensate inner Frame padding
            rightMargin=self.template_class.margins.right - REPORTLAB_INNER_FRAME_PADDING,
            bottomMargin=self.template_class.margins.bottom - REPORTLAB_INNER_FRAME_PADDING,
            leftMargin=self.template_class.margins.left - REPORTLAB_INNER_FRAME_PADDING,
        )
        self.elements: List[Flowable] = []

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the context manager closing the buffer."""
        self.buffer.close()

    def _build(self) -> None:
        """Build the PDF file.

        This method is called automatically when the document is saved to a file
        or when the bytes property is accessed.
        """
        self.doc._calc()
        frame = Frame(self.doc.leftMargin, self.doc.bottomMargin, self.doc.width, self.doc.height, id="normal")

        self.doc.addPageTemplates(
            [
                PageTemplate(id="First", frames=frame, pagesize=self.doc.pagesize),
                """
                PageTemplate(id="First", frames=frameT, onPage=onFirstPage, pagesize=self.pagesize),
                PageTemplate(id="Later", frames=frameT, onPage=onLaterPages, pagesize=self.pagesize),
                """,
            ]
        )
        """if onFirstPage is _doNothing and hasattr(self, "onFirstPage"):
            self.pageTemplates[0].beforeDrawPage = self.onFirstPage
        if onLaterPages is _doNothing and hasattr(self, "onLaterPages"):
            self.pageTemplates[1].beforeDrawPage = self.onLaterPages"""

        self.doc.build(self.elements, canvasmaker=Canvas)

    def _get_style(self, style_name: str, options: Optional[ElementOptions] = None) -> ParagraphStyle:
        if not options:
            return self.template._stylesheet[style_name]

        style_changes: Dict[str, Union[str, int]] = {}

        color = options.get("color")
        align = options.get("align")
        margins = get_margins(options or {})

        if color:
            style_changes["textColor"] = color

        if align:
            style_changes["alignment"] = {
                "left": TA_LEFT,
                "right": TA_RIGHT,
                "center": TA_CENTER,
                "justify": TA_JUSTIFY,
            }[align]

        if margins.top:
            style_changes["spaceBefore"] = margins.top

        if margins.right:
            style_changes["rightIndent"] = margins.right

        if margins.bottom:
            style_changes["spaceAfter"] = margins.bottom

        if margins.left:
            style_changes["leftIndent"] = margins.left

        if style_changes:
            style_name = self._get_substyle(style_name, str(style_changes), **style_changes)

        return self.template._stylesheet[style_name]

    def _get_substyle(self, style_name: str, substyle_name: str, **kwargs) -> str:
        substyle_name = f"{style_name}__{substyle_name}"
        if substyle_name not in self.template._stylesheet:
            parent_style = self.template._stylesheet[style_name]
            ParentStyleClass = parent_style.__class__
            substyle = ParentStyleClass(substyle_name, parent=self.template._stylesheet[style_name], **kwargs)
            self.template._stylesheet.add(substyle)
        return substyle_name

    def add_image(self):
        """Add an image to the document elements."""
        raise NotImplementedError

    def add_list(self, items: List[str], style: str, options: Optional[ElementOptions] = None) -> None:
        """Add a list to the document elements.

        Args:
            items: The list of items to add.
            style: The style to use for the list.
            options: The options to use for the list.
        """
        if not style or style not in self.template._stylesheet:
            raise ValueError("Valid style must be specified for `add_paragraph`")

        for text in items:
            self.add_paragraph(text, style=style, options=options)

    def add_page_break(self) -> None:
        """Add a page break to the document elements."""
        self.elements.append(PageBreak())

    def add_paragraph(self, text: str, *, style: str, options: Optional[ElementOptions] = None) -> None:
        """Add a paragraph to the document elements.

        Args:
            text: The text to add.
            style: The style to use for the paragraph.
            options: The options to use for the paragraph.
        """
        if not style or style not in self.template._stylesheet:
            raise ValueError("Valid style must be specified for `add_paragraph`")

        self.elements.append(Paragraph(text, self._get_style(style, options)))

    def add_separator(self, height: int = 1, *, options: Optional[ElementOptions] = None) -> None:
        """Add a line separator to the document elements.

        color and margin options are used for the line.
        The line is added as a Drawing element, and the position of the line is determined by the
        margin options.

        Args:
            height: The height of the line.
            options: The options to use for the line.
        """
        margins = get_margins(options or {})

        if margins.top > 0:
            self.elements.append(Spacer(self.actual_width, margins.top))

        drawing = Drawing(self.actual_width, height)
        drawing.add(
            Line(
                margins.left,
                0,
                self.actual_width - margins.right,
                0,
                strokeColor=options.get("color", black) if options else black,
                strokeWidth=height,
            )
        )
        self.elements.append(drawing)

        if margins.bottom > 0:
            self.elements.append(Spacer(self.actual_width, margins.bottom))

    def add_spacer(self, height: int = 1) -> None:
        """Add a spacer to the document elements.

        Args:
            height: The height of the spacer.
        """
        self.elements.append(Spacer(self.actual_width, height))

    def add_table(self):
        """Add a table to the document elements."""
        raise NotImplementedError

    def h1(self, text: str, *, options: Optional[ElementOptions] = None):
        """Add a h1 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h1", options=options)

    def h2(self, text: str, *, options: Optional[ElementOptions] = None):
        """Add a h2 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h2", options=options)

    def h3(self, text: str, *, options: Optional[ElementOptions] = None):
        """Add a h3 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h3", options=options)

    def h4(self, text: str, *, options: Optional[ElementOptions] = None):
        """Add a h4 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h4", options=options)

    def h5(self, text: str, *, options: Optional[ElementOptions] = None):
        """Add a h5 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h5", options=options)

    def h6(self, text: str, *, options: Optional[ElementOptions] = None):
        """Add a h6 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h6", options=options)

    def p(self, text: str, *, options: Optional[ElementOptions] = None):
        """Add a paragraph to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the paragraph.
        """
        return self.add_paragraph(text, style="p", options=options)

    def br(self):
        """Add a line break to the document elements."""
        self.add_spacer(12)  # TODO: this should be linked with the line height, which should be defined somewhere

    def hr(self, *, height: int = 1, options: Optional[ElementOptions] = None) -> None:
        """Add a horizontal line to the document elements.

        Args:
            height: The height of the line.
            options: The options to use for the line.
        """
        self.add_separator(height, options=options)

    def ol(self, items: List[str], options: Optional[ElementOptions] = None):
        """Add an ordered list to the document elements."""
        return self.add_list(items, "ol", options)

    def ul(self, items: List[str], options: Optional[ElementOptions] = None):
        """Add an unordered list to the document elements."""
        return self.add_list(items, "ul", options)

    @property
    def actual_width(self) -> int:
        """Return the actual width of the document."""
        return self.doc.width - (REPORTLAB_INNER_FRAME_PADDING * 2)

    @property
    def default_font(self) -> Optional[Font]:
        """Return the default font."""
        return self.template.default_font

    @property
    def bytes(self) -> bytes:
        """Return the bytes of the document."""
        self._build()
        return self.buffer.getvalue()

    def save_as(self, file_path: Union[Path, str]) -> None:
        """Save the document to a file.

        Args:
            file_path: The path to the file to save the document to.
        """
        with open(file_path, "wb") as f:
            f.write(self.bytes)
