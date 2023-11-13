"""Test the pdfino.main module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from pdfino.main import Document, Template
from pdfino.type_definitions import Font, Margins


FONT_FOLDER = Path(__file__).parent / "fonts"


class TemplateForTest(Template):
    """Test Template class."""

    fonts = [Font("Lexend", normal=FONT_FOLDER / "Lexend-ExtraLight.ttf", default=True)]


class TemplateForBrokenTest(Template):
    """Test a Template class with broken fonts."""

    fonts = [
        Font("Lexend", normal=FONT_FOLDER / "Lexend-ExtraLight-Broken.ttf", default=True),
        Font("Lexend", normal=FONT_FOLDER / "Lexend-ExtraLight-Broken.ttf", default=True),
    ]


def test_template_init():
    """Test the initialization of the Template class."""
    template = Template()
    assert template.pagesize == (595.2755905511812, 841.8897637795277)
    assert template.margins == Margins(42.51968503937008, 42.51968503937008, 42.51968503937008, 42.51968503937008)
    assert template.fonts == []
    assert template.use_sample_stylesheet
    assert template.styles == []
    assert template.default_font is None


def test_template_register_fonts():
    """Test the _register_fonts method of the Template class."""
    TemplateForTest()


def test_template_register_fonts_broken():
    """Test the _register_fonts method of the Template class with broken fonts."""
    with pytest.raises(ValueError):
        TemplateForBrokenTest()


def test_document_init():
    """Test the initialization of the Document class."""
    document = Document()
    assert document.template_class == Template
    assert isinstance(document.template, Template)
    assert document.elements == []


def test_document_add_paragraph():
    """Test the add_paragraph method of the Document class."""
    text = "Test paragraph"
    style = "p"

    doc = Document()
    doc.add_paragraph(text, style=style)

    assert len(doc.elements) == 1


def test_add_paragraph():
    """Test the add_paragraph method of the Document class."""
    with patch("pdfino.main.Paragraph") as mock_paragraph:
        doc = Document()
        style = "BodyText"
        text = "Test paragraph"
        doc.add_paragraph(text, style=style)

    mock_paragraph.assert_called_once_with(text, doc._get_style(style, None))
    assert mock_paragraph.return_value in doc.elements


def test_add_paragraph_invalid_style():
    """Test the add_paragraph method with an invalid style."""
    doc = Document()
    style = "InvalidStyle"
    text = "Test paragraph"

    with pytest.raises(ValueError):
        doc.add_paragraph(text, style=style)


@pytest.mark.parametrize(
    "method_name,style",
    [
        ("h1", "h1"),
        ("h2", "h2"),
        ("h3", "h3"),
        ("h4", "h4"),
        ("h5", "h5"),
        ("h6", "h6"),
        ("p", "p"),
    ],
)
def test_magic_methods(method_name, style):
    """Test the heading methods of the Document class."""
    with patch.object(Document, "add_paragraph") as mock_add_paragraph:
        doc = Document()
        text = "Test heading"
        method = getattr(doc, method_name)
        method(text)

    # Check if add_paragraph was called with the correct style
    mock_add_paragraph.assert_called_once_with(text, style=style, options=None)
