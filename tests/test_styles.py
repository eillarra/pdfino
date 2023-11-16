"""Test styling in the pdfino.main module."""

import pytest

from pdfino.main import Document, Template
from pdfino.styles import TA_LEFT, TA_RIGHT, colors, get_modified_style, get_reportlab_kwargs, get_sample_stylesheet
from pdfino.type_definitions import Style


@pytest.mark.parametrize(
    "options, expected",
    [
        (
            {
                "color": "#000000",
                "align": "left",
                "margin_top": 20,
                "margin_right": 10,
                "margin_bottom": 30,
                "margin_left": 40,
            },
            {
                "textColor": colors.HexColor("#000000"),
                "alignment": TA_LEFT,
                "spaceBefore": 20,
                "rightIndent": 10,
                "spaceAfter": 30,
                "leftIndent": 40,
            },
        ),
        (
            {"color": "red", "align": "right"},
            {
                "textColor": colors.red,
                "alignment": TA_RIGHT,
            },
        ),
        (
            {
                "color": "red",
                "margins": (20, 10, 30, 40),
            },
            {
                "textColor": colors.red,
                "spaceBefore": 20,
                "rightIndent": 10,
                "spaceAfter": 30,
                "leftIndent": 40,
            },
        ),
    ],
)
def test_get_reportlab_kwargs(options, expected):
    """Test the get_reportlab_kwargs function."""
    result = get_reportlab_kwargs(options)
    assert result == expected


def test_modified_styles():
    """Test the modification of styles via options."""
    stylesheet = get_sample_stylesheet(font_size=10)
    assert stylesheet["p"].textColor == colors.black

    modified_style = get_modified_style(stylesheet, "p", {"color": "red"})
    assert modified_style.textColor == colors.red
    assert modified_style.name == "p__color_red"


def test_custom_styles():
    """Test the initialization of styles in a Template class."""

    class CustomTemplate(Template):
        """Test Template class."""

        styles = [
            Style("h3", font_size=20, options={"margin_top": 20, "color": "#000000"}),
        ]

    doc = Document(template=CustomTemplate())
    doc.h3("Hello world")

    assert len(doc.elements) == 1
