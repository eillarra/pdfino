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


BASE_FONT_SIZE = 12
BASE_LINE_HEIGHT = 1.35


def get_reportlab_kwargs(options: "ElementOptions") -> Dict[str, Union[str, int, None]]:
    """Get ReportLab kwargs from the options of an element.

    Args:
        options: Options for an element.

    Returns:
        ReportLab kwargs that can be applied to a ReportLab style.
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
    """Get a modified version of a style, based on the options of the given style."""
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
    """Returns a base stylesheet object.

    It only includes a base paragraph style and a base list style.
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
    """Returns a sample stylesheet object.

    Based on `reportlab.lib.styles.getSampleStyleSheet` but with
    some changes to make it more fino.
    """
    base_font_name = default_font.name if default_font else canvas_basefontname
    base_font_name_bold = tt2ps(base_font_name, 1, 0)
    base_font_name_italic = tt2ps(base_font_name, 0, 1)
    base_font_name_bold_italic = tt2ps(base_font_name, 1, 1)

    stylesheet = get_base_stylesheet(font_size, line_height, default_font)

    stylesheet.add(
        ParagraphStyle(
            name="heading1",
            parent=stylesheet["normal"],
            fontName=base_font_name_bold,
            fontSize=18,
            leading=22,
            spaceAfter=6,
        ),
        alias="h1",
    )

    stylesheet.add(
        ParagraphStyle(
            name="heading2",
            parent=stylesheet["normal"],
            fontName=base_font_name_bold,
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=6,
        ),
        alias="h2",
    )

    stylesheet.add(
        ParagraphStyle(
            name="heading3",
            parent=stylesheet["normal"],
            fontName=base_font_name_bold_italic,
            fontSize=12,
            leading=14,
            spaceBefore=12,
            spaceAfter=6,
        ),
        alias="h3",
    )

    stylesheet.add(
        ParagraphStyle(
            name="heading4",
            parent=stylesheet["normal"],
            fontName=base_font_name_bold_italic,
            fontSize=10,
            leading=12,
            spaceBefore=10,
            spaceAfter=4,
        ),
        alias="h4",
    )

    stylesheet.add(ParagraphStyle(name="paragraph", parent=stylesheet["normal"]), alias="p")

    stylesheet.add(
        ParagraphStyle(name="bullet", parent=stylesheet["normal"], firstLineIndent=0, spaceBefore=3), alias="bu"
    )

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
            parent=None,
            leftIndent=18,
            rightIndent=0,
            bulletAlign="left",
            bulletType="1",
            bulletColor=colors.black,
            bulletFontName="Helvetica",
            bulletFontSize=12,
            bulletOffsetY=0,
            bulletDedent="auto",
            bulletDir="ltr",
            bulletFormat=None,
            # start='1 a A i I'.split(),
            start=None,
        ),
        alias="ol",
    )

    return stylesheet
