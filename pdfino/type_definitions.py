"""Module for type definitions."""

from pathlib import Path
from typing import Literal, NamedTuple, Optional, TypedDict, Union

from reportlab.lib import pagesizes
from reportlab.lib.styles import LineStyle, ListStyle, ParagraphStyle


class Pagesize(NamedTuple):
    """NamedTuple representing a page size in points, for a resolution of 72 dpi.

    :param width: Width of the page in points.
    :param height: Height of the page in points.
    """

    width: float
    height: float

    @classmethod
    def from_name(cls, pagesize: str) -> "Pagesize":
        """Alternative constructor to create a Pagesize from a string, e.g. "A4".

        :param pagesize: Name of the pagesize, e.g. "A4".
        :return: Pagesize named tuple.
        :raises ValueError: If the pagesize is not a valid constant of `reportlab.lib.pagesizes`.
        """
        try:
            return cls(*getattr(pagesizes, pagesize.upper()))
        except AttributeError as exc:
            raise ValueError(f"Invalid pagesize: {pagesize}") from exc


class Margins(NamedTuple):
    """NamedTuple representing margins.

    :param top: Top margin.
    :param right: Right margin.
    :param bottom: Bottom margin.
    :param left: Left margin.
    """

    top: int
    right: int
    bottom: int
    left: int


class Font(NamedTuple):
    """NamedTuple representing a font definition with different variants.

    :param name: Name of the font.
    :param normal: Path to the normal variant of the font.
    :param bold: Path to the bold variant of the font.
    :param italic: Path to the italic variant of the font.
    :param bold_italic: Path to the bold italic variant of the font.
    :param default: Whether this font should be used as the default font for a Template.
    """

    name: str
    normal: Path
    bold: Optional[Path] = None
    italic: Optional[Path] = None
    bold_italic: Optional[Path] = None
    default: bool = False


class StyleOptions(TypedDict, total=False):
    """Styling options for an element.

    :param color: The color of the element.
    """

    color: str


class LayoutOptions(TypedDict, total=False):
    """Layout options for a page.

    :param margin_top: The top margin of the page.
    :param margin_right: The right margin of the page.
    :param margin_bottom: The bottom margin of the page.
    :param margin_left: The left margin of the page.
    :param margins: The margins of the page.
    """

    margin_top: int
    margin_right: int
    margin_bottom: int
    margin_left: int
    margins: Margins


class ElementOptions(LayoutOptions, StyleOptions, total=False):
    """All options for an element.

    :param align: The alignment of the element.
    """

    align: Literal["left", "right", "center", "justify"]


class Style(NamedTuple):
    """NamedTuple representing a style definition.

    :param name: Name of the style.
    :param parent: Parent style to inherit from (name of another style)
    :param options: Options for the style.
    :param font_name: Name of the font to use.
    :param font_size: Size of the font.
    :param line_height: Line height of the style, relative to the font size.
    :param allow_widows: Whether to allow widows (single lines at the end of a paragraph).
    :param hyphenate: Whether to hyphenate the text (requires `pyphen` to be installed)
    """

    name: str
    parent: Optional[str] = None
    options: Optional[ElementOptions] = None
    font_name: Optional[str] = None
    font_size: Optional[Union[int, float]] = None
    line_height: Optional[Union[int, float]] = None
    allow_widows: bool = False
    hyphenate: bool = False


ReportLabStyle = Union[ParagraphStyle, ListStyle, LineStyle]
OrderedBulletType = Literal["1", "a", "A", "i", "I"]
UnorderedBulletType = Literal["circle", "square", "blackstar", "sparkle", "diamond"]
