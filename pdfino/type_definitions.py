"""Module for type definitions."""

from pathlib import Path
from typing import Literal, NamedTuple, Optional, TypedDict, Union

from reportlab.lib import pagesizes
from reportlab.lib.styles import LineStyle, ListStyle, ParagraphStyle


class Pagesize(NamedTuple):
    """NamedTuple representing a page size in points, for a resolution of 72 dpi.

    Args:
        width: Width of the page.
        height: Height of the page.
    """

    width: float
    height: float

    @classmethod
    def from_name(cls, pagesize: str) -> "Pagesize":
        """Alternative constructor to create a Pagesize from a string, e.g. "A4".

        Args:
            pagesize: ReportLab pagesize.

        Returns:
            Pagesize named tuple.

        Raises:
            ValueError: If the pagesize is not a valid constant of `reportlab.lib.pagesizes`.
        """
        try:
            return cls(*getattr(pagesizes, pagesize.upper()))
        except AttributeError as exc:
            raise ValueError(f"Invalid pagesize: {pagesize}") from exc


class Margins(NamedTuple):
    """NamedTuple representing margins.

    Args:
        top: Top margin.
        right: Right margin.
        bottom: Bottom margin.
        left: Left margin.
    """

    top: int
    right: int
    bottom: int
    left: int


class Font(NamedTuple):
    """NamedTuple representing a font definition with different variants.

    Args:
        name: Name of the font.
        normal: Path to the normal variant of the font.
        bold: Path to the bold variant of the font.
        italic: Path to the italic variant of the font.
        bold_italic: Path to the bold italic variant of the font.
        default: Whether this font should be used as the default font for a Template.
    """

    name: str
    normal: Path
    bold: Optional[Path] = None
    italic: Optional[Path] = None
    bold_italic: Optional[Path] = None
    default: bool = False


class StyleOptions(TypedDict, total=False):
    """Styling options for an element."""

    color: str


class LayoutOptions(TypedDict, total=False):
    """Layout options for a page."""

    margin_top: int
    margin_right: int
    margin_bottom: int
    margin_left: int
    margins: Margins


class ElementOptions(LayoutOptions, StyleOptions, total=False):
    """All options for an element."""

    align: Literal["left", "right", "center", "justify"]


class Style(NamedTuple):
    """NamedTuple representing a style definition.

    Args:
        name: Name of the style.
        parent: Parent style to inherit from (name of another style)
        options: Options for the style.
        font_name: Name of the font to use.
        font_size: Size of the font.
        line_height: Line height of the style, relative to the font size.
    """

    name: str
    parent: Optional[str] = None
    options: Optional[ElementOptions] = None
    font_name: Optional[str] = None
    font_size: Optional[Union[int, float]] = None
    line_height: Optional[Union[int, float]] = None


ReportLabStyle = Union[ParagraphStyle, ListStyle, LineStyle]
OrderedBulletType = Literal["1", "a", "A", "i", "I"]
UnorderedBulletType = Literal["circle", "square", "blackstar", "sparkle", "diamond"]
