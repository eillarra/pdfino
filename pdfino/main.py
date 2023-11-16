"""Module for the main PDFino classes and API."""

import io
from pathlib import Path
from typing import Dict, List, Optional, Type, Union, get_args

from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.colors import black
from reportlab.lib.fonts import tt2ps
from reportlab.lib.pagesizes import mm
from reportlab.pdfbase.pdfmetrics import (
    getRegisteredFontNames,
    registerFont,
    registerFontFamily,
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.rl_config import canvas_basefontname

from .styles import (
    BASE_FONT_SIZE,
    BASE_LINE_HEIGHT,
    ParagraphStyle,
    get_base_stylesheet,
    get_modified_style,
    get_reportlab_kwargs,
    get_sample_stylesheet,
)
from .type_definitions import (
    ElementOptions,
    Font,
    Margins,
    OrderedBulletType,
    Pagesize,
    ReportLabStyle,
    Style,
    UnorderedBulletType,
)
from .utils import get_margins


REPORTLAB_INNER_FRAME_PADDING = 6


class Template:
    """A template that can be used to generate a PDF file."""

    pagesize: Pagesize = Pagesize.from_name("A4")
    margins: Margins = Margins(15 * mm, 15 * mm, 15 * mm, 15 * mm)
    fonts: List[Font] = []
    font_size: int = BASE_FONT_SIZE
    line_height: float = BASE_LINE_HEIGHT
    use_sample_stylesheet: bool = True
    styles: List[Union[Style, ParagraphStyle]] = []

    def __init__(self) -> None:
        """Initialize the template."""
        self._register_fonts()
        self._create_stylesheet()
        self._register_styles(self.styles)

    def _register_fonts(self) -> None:
        for font in self.fonts:
            try:
                if not font.normal or not font.normal.is_file():
                    raise ValueError(f"Font {font.name} must have a normal variant which is an existing file.")
            except AttributeError as exc:
                raise ValueError(f"Font {font.name} must have a normal variant which is an existing file.") from exc

            registerFont(TTFont(font.name, font.normal))

            variants = [
                ("-Bold", font.bold),
                ("-Italic", font.italic),
                ("-BoldItalic", font.bold_italic),
            ]

            for suffix, variant in variants:
                if variant:
                    if variant.is_file():
                        registerFont(TTFont(f"{font.name}{suffix}", variant))
                    else:
                        raise ValueError(f"Font file {variant} ({suffix}) does not exist.")

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

    def _create_stylesheet(self) -> None:
        if self.use_sample_stylesheet:
            self._stylesheet = get_sample_stylesheet(
                font_size=self.font_size, line_height=self.line_height, default_font=self.default_font
            )
            self._replace_default_fonts()
        else:
            self._stylesheet = get_base_stylesheet(
                font_size=self.font_size, line_height=self.line_height, default_font=self.default_font
            )

    def _register_styles(self, styles: List[Union[Style, ParagraphStyle]]) -> None:
        for style in styles:
            if isinstance(style, Style):
                if style.font_name and style.font_name not in getRegisteredFontNames():
                    raise ValueError(f"Font {style.font_name} is not registered.")
                reportlab_style = self._style_to_reportlab(style)
            elif isinstance(style, ParagraphStyle):  # add more types here
                reportlab_style = style

            try:
                self._stylesheet.add(reportlab_style)
            except KeyError:
                self._stylesheet[style.name].__dict__.update(reportlab_style.__dict__)

    def _style_to_reportlab(self, style: Style) -> ParagraphStyle:
        if not style.name:
            raise ValueError("Style must have a name.")

        default_font_name = self.default_font.name if self.default_font else canvas_basefontname
        default_font_size = self.font_size
        default_line_height = self.line_height

        try:
            parent = self.stylesheet[style.parent] if style.parent else None
            default_font_name = parent.fontName if parent else default_font_name
            default_font_size = parent.fontSize if parent else default_font_size
            default_line_height = parent.leading / parent.fontSize if parent else default_line_height
        except KeyError as exc:
            raise ValueError(f"Parent style {style.parent} does not exist.") from exc

        font_name = style.font_name if style.font_name else default_font_name
        font_size = style.font_size if style.font_size else default_font_size
        leading = style.line_height * font_size if style.line_height else default_line_height * font_size

        return ParagraphStyle(
            style.name.lower(),
            parent=parent,
            fontName=font_name,
            fontSize=font_size,
            leading=leading,
            **get_reportlab_kwargs(style.options or {}),
        )

    @property
    def default_font(self) -> Optional[Font]:
        """Return the default font."""
        return next((font for font in self.fonts if font.default), None)

    @property
    def stylesheet(self) -> Dict[str, ReportLabStyle]:
        """Return the indexed stylesheet."""
        return {**self._stylesheet.byName, **self._stylesheet.byAlias}


class Document:
    """A PDF document."""

    template_class: Type[Template] = Template
    styles: List[Union[Style, ParagraphStyle]] = []

    def __init__(self, *, template: Optional[Template] = None) -> None:
        """Initialize the document."""
        self.template = template if template else self.template_class()
        self.doc = BaseDocTemplate(
            None,
            pagesize=self.template_class.pagesize,
            topMargin=self.template_class.margins.top - REPORTLAB_INNER_FRAME_PADDING,  # compensate inner Frame padding
            rightMargin=self.template_class.margins.right - REPORTLAB_INNER_FRAME_PADDING,
            bottomMargin=self.template_class.margins.bottom - REPORTLAB_INNER_FRAME_PADDING,
            leftMargin=self.template_class.margins.left - REPORTLAB_INNER_FRAME_PADDING,
        )
        self.elements: List[Flowable] = []
        self.template._register_styles(self.styles)

    def _build(self) -> bytes:
        buffer = io.BytesIO()
        frame = Frame(self.doc.leftMargin, self.doc.bottomMargin, self.doc.width, self.doc.height)

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

        self.doc.build(
            self.elements[:],
            filename=buffer,
            canvasmaker=Canvas,
        )

        data = buffer.getvalue()
        buffer.close()

        return data

    def _get_style(self, style_name: str, options: Optional[ElementOptions] = None) -> ParagraphStyle:
        style_name = style_name.lower()

        if not options:
            return self.template.stylesheet[style_name]

        return get_modified_style(self.template._stylesheet, style_name, options)

    def add(self, reportlab_element: Flowable) -> None:
        """Add a ReportLab Flowable directly to the document elements.

        Args:
            reportlab_element: The flowable to add.
        """
        self.elements.append(reportlab_element)

    def add_image(self) -> None:
        """Add an image to the document elements."""
        raise NotImplementedError

    def add_list(
        self,
        items: List[str],
        *,
        bullet_type: Union[OrderedBulletType, UnorderedBulletType],
        style: str,
        options: Optional[ElementOptions] = None,
        item_options: Optional[ElementOptions] = None,
    ) -> None:
        """Add a list to the document elements.

        Args:
            items: The list of items to add.
            bullet_type: The type of bullet to use for the list.
            style: The style to use for the list.
            options: The options to use for the list.
            item_options: The options to use for the list items.
        """
        if not style or style not in self.template._stylesheet:
            raise ValueError("Valid style must be specified for `add_list`")

        list_items = [
            ListItem(
                Paragraph(text, self._get_style("p", item_options)),
                bulletColor=item_options.get("color", black) if item_options else black,
            )
            for text in items
        ]

        if bullet_type in get_args(UnorderedBulletType):
            use_bullet = "bullet"
            start = bullet_type
        elif bullet_type in get_args(OrderedBulletType):
            use_bullet = bullet_type
            start = None
        else:
            raise ValueError(f"Invalid bullet type {bullet_type}")

        self.elements.append(
            ListFlowable(
                list_items, bulletFontSize=8, bulletType=use_bullet, start=start, style=self._get_style(style, options)
            )
        )

        # TODO ^^^^^^: see which styles are used where (ListStyles and ParagraphStyles) and clean up

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

    def add_table(self) -> None:
        """Add a table to the document elements."""
        raise NotImplementedError

    def h1(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a h1 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h1", options=options)

    def h2(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a h2 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h2", options=options)

    def h3(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a h3 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h3", options=options)

    def h4(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a h4 to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the header.
        """
        return self.add_paragraph(text, style="h4", options=options)

    def p(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a paragraph to the document elements.

        Args:
            text: The text to add.
            options: The options to use for the paragraph.
        """
        return self.add_paragraph(text, style="p", options=options)

    def br(self) -> None:
        """Add a line break to the document elements."""
        self.add_spacer(12)  # TODO: this should be linked with the line height, which should be defined somewhere

    def hr(self, *, height: int = 1, options: Optional[ElementOptions] = None) -> None:
        """Add a horizontal line to the document elements.

        Args:
            height: The height of the line.
            options: The options to use for the line.
        """
        self.add_separator(height, options=options)

    def ol(
        self,
        items: List[str],
        *,
        bullet_type: OrderedBulletType = "1",
        options: Optional[ElementOptions] = None,
        item_options: Optional[ElementOptions] = None,
    ) -> None:
        """Add an ordered list to the document elements."""
        return self.add_list(items, bullet_type=bullet_type, style="ol", options=options, item_options=item_options)

    def ul(
        self,
        items: List[str],
        *,
        bullet_type: UnorderedBulletType = "circle",
        options: Optional[ElementOptions] = None,
        item_options: Optional[ElementOptions] = None,
    ) -> None:
        """Add an unordered list to the document elements."""
        return self.add_list(items, bullet_type=bullet_type, style="ul", options=options, item_options=item_options)

    @property
    def actual_width(self) -> float:
        """Return the actual width of the document."""
        return self.doc.width - (REPORTLAB_INNER_FRAME_PADDING * 2)

    @property
    def bytes(self) -> bytes:
        """Return the bytes data of the document."""
        return self._build()

    @property
    def stylesheet(self) -> Dict[str, ReportLabStyle]:
        """Return the indexed stylesheet."""
        return self.template.stylesheet

    def save_as(self, file_path: Union[Path, str]) -> None:
        """Save the document to a file.

        Args:
            file_path: The path to the file to save the document to.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        with open(file_path, "wb") as f:
            f.write(self.bytes)
