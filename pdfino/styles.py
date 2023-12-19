"""Sample stylesheet and style utils for PDFino."""

from typing import TYPE_CHECKING, Dict, Optional, Union

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.fonts import tt2ps
from reportlab.lib.styles import ListStyle, ParagraphStyle
from reportlab.lib.styles import StyleSheet1 as Stylesheet
from reportlab.rl_config import canvas_basefontname

from .utils import get_margins


if TYPE_CHECKING:
    from .type_definitions import ElementOptions, Font


BASE_FONT_SIZE = 10
BASE_LINE_HEIGHT = 1.5


def get_reportlab_kwargs(options: "ElementOptions") -> Dict[str, Union[str, int, None]]:
    """Get ReportLab kwargs from the options of an element.

    :param options: Options for an element.
    :return: ReportLab kwargs that can be applied to a ReportLab style.
    """
    reportlab_kwargs: Dict[str, Union[str, int, None]] = {}

    color = options.get("color")
    align = options.get("align")
    margins = get_margins(options or {})

    if color:
        try:
            color = getattr(colors, color)
        except AttributeError:
            color = colors.HexColor(color)
        reportlab_kwargs["textColor"] = color

    if align:
        reportlab_kwargs["alignment"] = {
            "left": TA_LEFT,
            "right": TA_RIGHT,
            "center": TA_CENTER,
            "justify": TA_JUSTIFY,
        }[align]

    if margins.top:
        reportlab_kwargs["spaceBefore"] = margins.top

    if margins.right:
        reportlab_kwargs["rightIndent"] = margins.right

    if margins.bottom:
        reportlab_kwargs["spaceAfter"] = margins.bottom

    if margins.left:
        reportlab_kwargs["leftIndent"] = margins.left

    return reportlab_kwargs


def get_modified_style(stylesheet: Stylesheet, style_name: str, options: "ElementOptions") -> ParagraphStyle:
    """Get a modified version of a style, based on the options of the given style.

    :param stylesheet: A ReportLab stylesheet object.
    :param style_name: The name of the style to modify.
    :param options: Options for an element.
    :return: A modified version of the given style.
    """
    style_changes = get_reportlab_kwargs(options)

    if style_changes:
        pretty_options = "__".join(f"{k}_{v}" for k, v in options.items())
        substyle_name = f"{style_name}__{pretty_options}".lower()

        if substyle_name not in stylesheet:
            parent_style = stylesheet[style_name]
            ParentStyleClass = parent_style.__class__
            substyle = ParentStyleClass(substyle_name, parent=stylesheet[style_name], **style_changes)
            stylesheet.add(substyle, alias=substyle_name)

    return stylesheet[substyle_name]


def get_base_stylesheet(
    font_size: int = BASE_FONT_SIZE, line_height: float = BASE_LINE_HEIGHT, default_font: Optional["Font"] = None
) -> Stylesheet:
    """Get a base stylesheet object.

    It only includes a base paragraph style and a base list style.

    :param font_size: The base font size.
    :param line_height: The base line height.
    :param default_font: The default font to use.
    :return: A base stylesheet object.
    """
    stylesheet = Stylesheet()

    base_font_name = default_font.name if default_font else canvas_basefontname
    base_font_name_bold = tt2ps(base_font_name, 1, 0)
    base_font_name_italic = tt2ps(base_font_name, 0, 1)
    base_font_name_bold_italic = tt2ps(base_font_name, 1, 1)

    leading = font_size * line_height

    stylesheet.add(ParagraphStyle(name="normal", fontName=base_font_name, fontSize=font_size, leading=leading))
    stylesheet.add(ParagraphStyle(name="bodytext", parent=stylesheet["normal"]), alias="body")
    stylesheet.add(ParagraphStyle(name="bold", parent=stylesheet["bodytext"], fontName=base_font_name_bold))
    stylesheet.add(ParagraphStyle(name="italic", parent=stylesheet["bodytext"], fontName=base_font_name_italic))

    return stylesheet


def get_sample_stylesheet(
    font_size: int = BASE_FONT_SIZE, line_height: float = BASE_LINE_HEIGHT, default_font: Optional["Font"] = None
) -> Stylesheet:
    """Get a sample stylesheet object.

    Based on `reportlab.lib.styles.getSampleStyleSheet` but with some changes to make it more fino.

    :param font_size: The base font size.
    :param line_height: The base line height.
    :param default_font: The default font to use.
    :return: A sample stylesheet object.
    """
    base_font_name = default_font.name if default_font else canvas_basefontname
    base_font_name_bold = tt2ps(base_font_name, 1, 0)
    base_font_name_italic = tt2ps(base_font_name, 0, 1)
    base_font_name_bold_italic = tt2ps(base_font_name, 1, 1)

    stylesheet = get_base_stylesheet(font_size, line_height, default_font)

    headings = [
        ("heading1", base_font_name_bold, 18, 22, 6),
        ("heading2", base_font_name_bold, 14, 18, 6),
        ("heading3", base_font_name_bold_italic, 12, 14, 6),
        ("heading4", base_font_name_bold_italic, 10, 12, 4),
    ]

    for name, font_name, h_font_size, leading, space_after in headings:
        stylesheet.add(
            ParagraphStyle(
                name=name,
                parent=stylesheet["normal"],
                fontName=font_name,
                fontSize=h_font_size,
                leading=leading,
                spaceAfter=space_after,
            ),
            alias=f"{name[0]}{name[-1]}",
        )

    stylesheet.add(ParagraphStyle(name="paragraph", parent=stylesheet["normal"], allowWidows=False), alias="p")

    stylesheet.add(
        ParagraphStyle(
            name="definition",
            parent=stylesheet["normal"],
            firstLineIndent=0,
            leftIndent=36,
            bulletIndent=0,
            spaceBefore=6,
            bulletFontName=base_font_name_bold_italic,
        ),
        alias="df",
    )

    stylesheet.add(
        ParagraphStyle(
            name="code",
            parent=stylesheet["normal"],
            fontName="Courier",
            fontSize=8,
            leading=8.8,
            firstLineIndent=0,
            leftIndent=36,
            hyphenationLang="",
        )
    )

    stylesheet.add(
        ListStyle(
            name="unorderedlist",
            parent=None,
            fontName="Courier",
            fontSize=8,
            leading=8.8,
            leftIndent=18,
            rightIndent=0,
            bulletAlign="left",
            bulletType="circle",
            bulletColor=colors.black,
            bulletFontName="Helvetica",
            bulletFontSize=12,
            bulletOffsetY=0,
            bulletDedent="auto",
            bulletDir="ltr",
            bulletFormat=None,
            # start='circle square blackstar sparkle disc diamond'.split(),
            start=None,
        ),
        alias="ul",
    )

    stylesheet.add(
        ListStyle(
            name="orderedlist",
            parent=stylesheet["unorderedlist"],
            bulletType="1",
        ),
        alias="ol",
    )

    return stylesheet
