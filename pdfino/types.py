"""Module for type definitions."""

from pathlib import Path
from typing import Literal, NamedTuple, Optional, TypedDict


class Margins(NamedTuple):
    """Margins of a page."""

    top: int
    right: int
    bottom: int
    left: int


class ElementOptions(TypedDict, total=False):
    """Options for an element."""

    color: str
    align: Literal["left", "right", "center", "justify"]
    margin_top: int
    margin_right: int
    margin_bottom: int
    margin_left: int
    margins: Margins


class Font(NamedTuple):
    """Font definition, with normal, bold, italic and bold_italic variant paths."""

    name: str
    normal: Path
    bold: Optional[Path] = None
    italic: Optional[Path] = None
    bold_italic: Optional[Path] = None
    default: bool = False


class Style(NamedTuple):
    """Style."""

    name: str
    font_name: str
    font_size: int
    color: str
