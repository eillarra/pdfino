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
from reportlab.platypus import (
    CondPageBreak,
    Flowable,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.rl_config import canvas_basefontname
from svglib.svglib import svg2rlg

from .platypus import Canvas, DocTemplate, OutlineDocTemplate
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


def make_paragraph(text: str, style: str, options: Optional[ElementOptions] = None) -> Paragraph:
    """Make a paragraph.

    :param text: The text to add.
    :param style: The style to use for the paragraph.
    :param options: The options to use for the paragraph.
    """
    return Paragraph(text, style=style, **get_reportlab_kwargs(options or {}))


class LeftFloatSVG(Flowable):
    # TODO: abstract these floating elements
    def __init__(self, svg_path, max_width, max_height):
        super().__init__()
        self.svg = svg2rlg(svg_path)
        drawing_width, drawing_height = self.svg.minWidth(), self.svg.height
        self.svg.scale(max_height / drawing_height, max_height / drawing_height)

    def draw(self):
        # float to the left of the frame
        self.svg.drawOn(self.canv, -15 * mm, -10 * mm)


class Template:
    """A template that can be used to generate a PDF file."""

    pagesize: Pagesize = Pagesize.from_name("A4")
    margins: Margins = Margins(15 * mm, 15 * mm, 15 * mm, 15 * mm)
    columns: int = 1
    column_spacing: float = 5 * mm

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

    def _register_styles(self, styles: List[Union[Style, ParagraphStyle]], language: str = "en") -> None:
        for style in styles:
            if isinstance(style, Style):
                if style.font_name and style.font_name not in getRegisteredFontNames():
                    raise ValueError(f"Font {style.font_name} is not registered.")
                reportlab_style = self._style_to_reportlab(style, language)
            elif isinstance(style, ParagraphStyle):  # add more types here
                reportlab_style = style

            try:
                self._stylesheet.add(reportlab_style)
            except KeyError:
                self._stylesheet[style.name].__dict__.update(reportlab_style.__dict__)

    def _style_to_reportlab(self, style: Style, language: str = "en") -> ParagraphStyle:
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
            hyphenationLang=language if style.hyphenate else None,
            allowWidows=style.allow_widows,
            **get_reportlab_kwargs(style.options or {}),
        )

    @property
    def default_font(self) -> Optional[Font]:
        """The default font."""
        return next((font for font in self.fonts if font.default), None)

    @property
    def stylesheet(self) -> Dict[str, ReportLabStyle]:
        """The indexed stylesheet."""
        return {**self._stylesheet.byName, **self._stylesheet.byAlias}


class Document:
    """A PDF document.

    :param template: The template to use for the document.
    :param canvas_class: The class to use for the document canvas.
    :param title: The title of the document.
    :param author: The author of the document.
    :param language: The language of the document.
    """

    template_class: Type[Template] = Template
    canvas_class: Type[Canvas] = Canvas
    styles: List[Union[Style, ParagraphStyle]] = []

    def __init__(
        self,
        *,
        template: Optional[Template] = None,
        canvas_class: Optional[Type[Canvas]] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        language: str = "en",
        outline: bool = False,
    ) -> None:
        """Initialize the document."""
        self.language = language or "en"
        self.outline = outline
        self.template = template if template else self.template_class()
        self.template._register_styles(self.styles, language=self.language)
        self.elements: List[Flowable] = []

        if canvas_class:
            self.canvas_class = canvas_class

        self.doc = (OutlineDocTemplate if outline else DocTemplate)(
            None,
            pagesize=self.template.pagesize,
            topMargin=self.template.margins.top - REPORTLAB_INNER_FRAME_PADDING,  # compensate inner Frame padding
            rightMargin=self.template.margins.right - REPORTLAB_INNER_FRAME_PADDING,
            bottomMargin=self.template.margins.bottom - REPORTLAB_INNER_FRAME_PADDING,
            leftMargin=self.template.margins.left - REPORTLAB_INNER_FRAME_PADDING,
            title=title,
            author=author,
        )

        self._create_multi_column_template()

    def _create_multi_column_template(self):
        columns, spacing = self.template.columns, self.template.column_spacing
        width, height = self.template.pagesize
        top_margin, right_margin, bottom_margin, left_margin = self.template.margins
        total_column_space = width - left_margin - right_margin - ((columns - 1) * spacing)
        self._column_width = total_column_space / columns

        frames = []

        for i in range(columns):
            frame_left_margin = left_margin + (i * (self._column_width + spacing))
            frame = Frame(frame_left_margin, bottom_margin, self._column_width, height - top_margin - bottom_margin)
            frames.append(frame)

        multi_column_template = PageTemplate(id="main", frames=frames)
        self.doc.addPageTemplates([multi_column_template])

    def _build(self) -> bytes:
        buffer = io.BytesIO()

        if self.outline:
            self.doc.multiBuild(self.elements[:], filename=buffer, canvasmaker=self.canvas_class)
        else:
            self.doc.build(self.elements[:], filename=buffer, canvasmaker=self.canvas_class)

        data = buffer.getvalue()
        buffer.close()

        return data

    def _get_style(self, style_name: str, options: Optional[ElementOptions] = None) -> ParagraphStyle:
        style_name = style_name.lower()

        if not options:
            return self.template.stylesheet[style_name]

        return get_modified_style(self.template._stylesheet, style_name, options)

    def add_custom_templates(self, templates: List[PageTemplate]) -> None:
        """Add custom templates to the document.

        :param templates: The list of ReportLab templates to add.
        """
        self.doc.addPageTemplates(templates)

    def use_template(self, template_name) -> None:
        """Change the template of the document.

        :param template_name: The name of the template to use.
        """
        self.elements.append(NextPageTemplate(template_name))

    def add(self, reportlab_element: Flowable, *, keep_with_next: bool = False) -> None:
        """Add a ReportLab Flowable directly to the document elements.

        :param reportlab_element: The ReportLab Flowable to add.
        :param keep_with_next: Whether to keep the element with the next one.
        """
        el = reportlab_element
        el.keepWithNext = keep_with_next
        self.elements.append(el)

    def add_image(
        self, image_path: str, *, max_height: float = None, max_width: float = None, keep_with_next: bool = False
    ) -> None:
        """Add an image to the document.

        The image is scaled to fit the column width.

        :param image_path: The path to the image file.
        :param max_height: The maximum height of the image.
        :param max_width: The maximum width of the image.
        :param keep_with_next: Whether to keep the image with the next element.
        """
        img = Image(image_path)

        # If the image exceeds the max_height or max_width, scale it down
        if max_height and img.drawHeight > max_height:
            img.drawWidth = max_height * img.drawWidth / img.drawHeight
            img.drawHeight = max_height
        if max_width and img.drawWidth > max_width:
            img.drawHeight = max_width * img.drawHeight / img.drawWidth
            img.drawWidth = max_width

        # If the image exceeds the column width, scale it down
        if img.drawWidth > self.column_width:
            img.drawHeight = self.column_width * img.drawHeight / img.drawWidth
            img.drawWidth = self.column_width

        self.elements.append(CondPageBreak(img.drawHeight))
        self.add(img, keep_with_next=keep_with_next)

    def add_svg(self, svg_path: str, *, max_height: float = None, max_width: float = None) -> None:
        """Add a SVG drawing to the document.

        :param svg_path: The path to the SVG file.
        :param max_height: The maximum height of the drawing.
        :param max_width: The maximum width of the drawing.
        """
        self.elements.append(LeftFloatSVG(svg_path, max_width, max_height))

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

        :param items: The list of items to add.
        :param bullet_type: The type of bullet to use for the list.
        :param style: The style to use for the list.
        :param options: The options to use for the list.
        :param item_options: The options to use for the list items.
        """
        if not style or style not in self.template._stylesheet:
            raise ValueError("Valid style must be specified for `add_list`")

        class CustomListFlowable(ListFlowable):
            def drawBullet(self, bullet_str, **kwargs):
                bulletFontSize = self._get_style(style, options).fontSize * 0.5
                print(bulletFontSize)
                super().drawBullet(bullet_str, bulletFontSize=bulletFontSize, **kwargs)

        list_items = []

        for item in items:
            if isinstance(item, list):
                # If the item is a list, create a sublist
                sublist_items = []
                for subitem in item:
                    sublist_items.append(
                        ListItem(
                            Paragraph(subitem, self._get_style("p", item_options)),
                            bulletColor=item_options.get("color", black) if item_options else black,
                        )
                    )
                sublist = CustomListFlowable(
                    sublist_items,
                    bulletFontSize=8,
                    bulletType="bullet" if bullet_type == "circle" else "1",
                    start=None,
                    style=self._get_style(style, options),
                )
                list_items.append(ListItem(sublist))
            else:
                list_items.append(
                    ListItem(
                        Paragraph(item, self._get_style("p", item_options)),
                        bulletColor=item_options.get("color", black) if item_options else black,
                    )
                )

        if bullet_type in get_args(UnorderedBulletType):
            use_bullet = "bullet"
            start = None
        elif bullet_type in get_args(OrderedBulletType):
            use_bullet = "1"
            start = None
        else:
            raise ValueError(f"Invalid bullet type {bullet_type}")

        list_flowable = CustomListFlowable(
            list_items, bulletFontSize=8, bulletType=use_bullet, start=start, style=self._get_style(style, options)
        )
        self.elements.append(list_flowable)

        return list_flowable

    def add_list2(
        self,
        items: List[str],
        *,
        bullet_type: Union[OrderedBulletType, UnorderedBulletType],
        style: str,
        options: Optional[ElementOptions] = None,
        item_options: Optional[ElementOptions] = None,
    ) -> None:
        # Define a Paragraph style with a custom bullet character and font size
        bullet_style = ParagraphStyle(
            "BulletStyle",
            parent=self._get_style("p", options),
            bulletIndent=5,
            leftIndent=0,
            spaceBefore=0,
            spaceAfter=5,
        )

        # Create Paragraph instances for your list items using the custom style
        bullet_char = "•" if bullet_type == "circle" else "1"
        list_items = [Paragraph(item, bullet_style) for item in items]

        # Add the Paragraph instances to your document
        list_flowable = ListFlowable(list_items, bulletType="bullet" if bullet_type == "circle" else "1")
        self.elements.append(list_flowable)

    def add_list_from_markdown(
        self,
        markdown: str,
        *,
        style: str,
        options: Optional[ElementOptions] = None,
        item_options: Optional[ElementOptions] = None,
    ) -> None:
        try:
            from markdown_it import MarkdownIt
        except ImportError as exc:
            raise ImportError("The `markdown-it-py` package is required to use `add_list_from_markdown`") from exc

        md = MarkdownIt()
        tokens = md.parse(markdown)

        # Extract the list items from the tokens
        items = self._extract_list_items(tokens)

        # Determine the bullet type based on the first list item token
        first_list_item_token = next((token for token in tokens if token.type == "list_item_open"), None)
        bullet_type = "circle" if first_list_item_token and first_list_item_token.markup == "-" else "1"

        # Add the list to the document
        self.add_list(items, bullet_type=bullet_type, style=style, options=options, item_options=item_options)

    def _extract_list_items(self, tokens: list) -> list[str]:
        items = []
        sublist = []

        for token in tokens:
            if token.type == "list_item_open":
                sublist = []
            elif token.type == "list_item_close":
                items.append(" ".join(sublist))  # Join the sublist into a string
                sublist = []  # Clear the sublist
            elif token.type == "inline":
                sublist.append(token.content)
            elif token.type in ["bullet_list_open", "ordered_list_open"] and getattr(token, "children", None):
                sublist_items = self._extract_list_items(token.children)
                if sublist_items:
                    sublist.extend(sublist_items)

        return items

    def add_column_break(self) -> None:
        """Add a column break to the document elements."""
        self.elements.append(CondPageBreak(self.template.pagesize.height))

    def add_page_break(self) -> None:
        """Add a page break to the document elements."""
        self.elements.append(PageBreak())

    def add_header(self, text: str, *, style: str, options: Optional[ElementOptions] = None) -> None:
        """Add a header to the document elements.

        :param text: The text to add.
        :param style: The style to use for the header.
        :param options: The options to use for the header.
        """
        # FIXME: this is a hack to avoid jumping to a new frame when there is actually enough space
        # Theoretically we should be using `keep_with_next` here, but that doesn't do what you would expect
        self.elements.append(CondPageBreak(30 * mm))
        self.add_paragraph(text, style=style, options=options)

    def add_paragraph(self, text: str, *, style: str, options: Optional[ElementOptions] = None) -> None:
        """Add a paragraph to the document elements.

        :param text: The text to add.
        :param style: The style to use for the paragraph.
        :param options: The options to use for the paragraph.
        """
        if not style or style not in self.template._stylesheet:
            raise ValueError("Valid style must be specified for `add_paragraph`")

        self.add(
            Paragraph(text, self._get_style(style, options)),
            keep_with_next=(options or {}).get("keep_with_next", False),
        )

    def add_separator(self, height: int = 1, *, options: Optional[ElementOptions] = None) -> None:
        """Add a line separator to the document elements.

        Color and margin options are used for the line.
        The line is added as a Drawing element, and the position of the line is determined by the margin options.

        :param height: The height of the line.
        :param options: The options to use for the line.
        """
        separator_elements: List[Flowable] = []
        margins = get_margins(options or {})

        if margins.top > 0:
            separator_elements.append(Spacer(self.column_width, margins.top))

        drawing = Drawing(self.column_width, height)
        drawing.add(
            Line(
                margins.left,
                0,
                self.column_width - margins.right,
                0,
                strokeColor=options.get("color", black) if options else black,
                strokeWidth=height,
            )
        )
        separator_elements.append(drawing)

        if margins.bottom > 0:
            separator_elements.append(Spacer(self.column_width, margins.bottom))

        self.add(KeepTogether(separator_elements), keep_with_next=(options or {}).get("keep_with_next", True))

    def add_spacer(self, height: int = 1) -> None:
        """Add a spacer to the document elements.

        :param height: The height of the spacer.
        """
        self.elements.append(Spacer(self.actual_width, height))

    def add_table(self) -> None:
        """Add a table to the document elements."""
        raise NotImplementedError

    def h1(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a h1 to the document elements.

        :param text: The text to add.
        :param options: The options to use for the header.
        """
        return self.add_header(text, style="h1", options=options)

    def h2(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a h2 to the document elements.

        :param text: The text to add.
        :param options: The options to use for the header.
        """
        return self.add_header(text, style="h2", options=options)

    def h3(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a h3 to the document elements.

        :param text: The text to add.
        :param options: The options to use for the header.
        """
        return self.add_header(text, style="h3", options=options)

    def h4(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a h4 to the document elements.

        :param text: The text to add.
        :param options: The options to use for the header.
        """
        return self.add_header(text, style="h4", options=options)

    def p(self, text: str, *, options: Optional[ElementOptions] = None) -> None:
        """Add a paragraph to the document elements.

        :param text: The text to add.
        :param options: The options to use for the header.
        """
        return self.add_paragraph(text, style="p", options=options)

    def br(self) -> None:
        """Add a line break to the document elements."""
        self.add_paragraph("<br />", style="body")

    def hr(self, *, height: int = 1, options: Optional[ElementOptions] = None) -> None:
        """Add a horizontal line to the document elements.

        :param height: The height of the line.
        :param options: The options to use for the line.
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
        """The actual width of the document."""
        return self.doc.width - (REPORTLAB_INNER_FRAME_PADDING * 2)

    @property
    def column_width(self) -> float:
        """The width of the document columns."""
        return self._column_width - (REPORTLAB_INNER_FRAME_PADDING * 2)

    @property
    def bytes(self) -> bytes:
        """The bytes data of the document."""
        return self._build()

    @property
    def page_templates(self) -> List[PageTemplate]:
        """The templates of the document."""
        return self.doc.pageTemplates

    @property
    def stylesheet(self) -> Dict[str, ReportLabStyle]:
        """The indexed stylesheet."""
        return self.template.stylesheet

    def save_as(self, file_path: Union[Path, str]) -> None:
        """Save the document to a file.

        :param file_path: The path to the file to save the document to.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        with open(file_path, "wb") as f:
            f.write(self.bytes)
