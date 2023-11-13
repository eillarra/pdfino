"""Sample stylesheet for PDFINO."""

from typing import TYPE_CHECKING, Optional

from reportlab.lib.colors import black
from reportlab.lib.fonts import tt2ps
from reportlab.lib.styles import ListStyle, ParagraphStyle
from reportlab.lib.styles import StyleSheet1 as Stylesheet
from reportlab.rl_config import canvas_basefontname


if TYPE_CHECKING:
    from .types import Font


def get_sample_stylesheet(default_font: Optional["Font"] = None) -> Stylesheet:
    """Returns a sample stylesheet object.

    Based on `reportlab.lib.styles.getSampleStyleSheet` but with
    some changes to make it more fino.
    """
    base_font_name = default_font.name if default_font else canvas_basefontname
    base_font_name_bold = tt2ps(base_font_name, 1, 0)
    base_font_name_italic = tt2ps(base_font_name, 0, 1)
    base_font_name_bold_italic = tt2ps(base_font_name, 1, 1)

    stylesheet = Stylesheet()

    stylesheet.add(ParagraphStyle(name="Normal", fontName=base_font_name, fontSize=10, leading=12))
    stylesheet.add(ParagraphStyle(name="BodyText", parent=stylesheet["Normal"], spaceBefore=6))
    stylesheet.add(ParagraphStyle(name="Italic", parent=stylesheet["BodyText"], fontName=base_font_name_italic))

    stylesheet.add(
        ParagraphStyle(
            name="Heading1",
            parent=stylesheet["Normal"],
            fontName=base_font_name_bold,
            fontSize=18,
            leading=22,
            spaceAfter=6,
        ),
        alias="h1",
    )

    stylesheet.add(
        ParagraphStyle(
            name="Heading2",
            parent=stylesheet["Normal"],
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
            name="Heading3",
            parent=stylesheet["Normal"],
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
            name="Heading4",
            parent=stylesheet["Normal"],
            fontName=base_font_name_bold_italic,
            fontSize=10,
            leading=12,
            spaceBefore=10,
            spaceAfter=4,
        ),
        alias="h4",
    )

    stylesheet.add(
        ParagraphStyle(
            name="Heading5",
            parent=stylesheet["Normal"],
            fontName=base_font_name_bold,
            fontSize=9,
            leading=10.8,
            spaceBefore=8,
            spaceAfter=4,
        ),
        alias="h5",
    )

    stylesheet.add(
        ParagraphStyle(
            name="Heading6",
            parent=stylesheet["Normal"],
            fontName=base_font_name_bold,
            fontSize=7,
            leading=8.4,
            spaceBefore=6,
            spaceAfter=2,
        ),
        alias="h6",
    )

    stylesheet.add(
        ParagraphStyle(name="Bullet", parent=stylesheet["Normal"], firstLineIndent=0, spaceBefore=3), alias="bu"
    )

    stylesheet.add(
        ParagraphStyle(
            name="Definition",
            parent=stylesheet["Normal"],
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
            name="Code",
            parent=stylesheet["Normal"],
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
            name="UnorderedList",
            parent=None,
            leftIndent=18,
            rightIndent=0,
            bulletAlign="left",
            bulletType="1",
            bulletColor=black,
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
            name="OrderedList",
            parent=None,
            leftIndent=18,
            rightIndent=0,
            bulletAlign="left",
            bulletType="1",
            bulletColor=black,
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
