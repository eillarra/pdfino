"""Test the pdfino.main module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from pdfino.main import Document, Template
from pdfino.type_definitions import Font, Margins


FONT_FOLDER = Path(__file__).parent / "fonts"


def test_template_init():
    """Test the initialization of the Template class."""
    template = Template()
    assert template.pagesize == (595.2755905511812, 841.8897637795277)
    assert template.margins == Margins(42.51968503937008, 42.51968503937008, 42.51968503937008, 42.51968503937008)
    assert template.fonts == []
    assert template.use_sample_stylesheet
    assert template.styles == []
    assert template.default_font is None


@pytest.mark.parametrize(
    "font",
    [
        Font("Roboto", normal=FONT_FOLDER / "Roboto-Thin.ttf", default=True),
        Font("Roboto", normal=FONT_FOLDER / "Roboto-Thin.ttf", bold=FONT_FOLDER / "Roboto-Thin.ttf", default=True),
    ],
)
def test_template_register_fonts(font):
    """Test the _register methods of the Template class."""

    class TemplateWithFonts(Template):
        fonts = [font]

    TemplateWithFonts()


@pytest.mark.parametrize(
    "font",
    [
        Font("Roboto", normal=FONT_FOLDER / "Roboto-Thin-Broken.ttf", default=True),
        Font("Roboto", normal=FONT_FOLDER / "Roboto-Thin.ttf", bold=FONT_FOLDER / "Roboto-Thin-Bold.ttf", default=True),
        Font("Roboto", normal="fonts/Roboto-Thin-Broken.ttf", default=True),
    ],
)
def test_template_register_fonts_broken(font):
    """Test the _register_fonts method of the Template class with broken fonts."""

    class TemplateWithBrokenFonts(Template):
        fonts = [font]

    with pytest.raises(ValueError):
        TemplateWithBrokenFonts()


def test_document_init():
    """Test the initialization of the Document class."""
    doc = Document()
    assert doc.template_class == Template
    assert isinstance(doc.template, Template)
    assert doc.elements == []


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
        style = "BodyText".lower()
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
    "magic_method_name, style, method_name",
    [
        ("h1", "h1", "add_header"),
        ("h2", "h2", "add_header"),
        ("h3", "h3", "add_header"),
        ("h4", "h4", "add_header"),
        ("p", "p", "add_paragraph"),
    ],
)
def test_magic_methods(magic_method_name, style, method_name):
    """Test the heading methods of the Document class."""
    with patch.object(Document, method_name) as mock_method:
        doc = Document()
        text = "Test heading"
        method = getattr(doc, magic_method_name)
        method(text)

    mock_method.assert_called_once_with(text, style=style, options=None)


def test_save_as_file():
    """Test the save_as method of the Document class."""
    doc = Document()
    doc.h1("Test")
    doc.save_as("test.pdf")

    assert Path("test.pdf").exists()
    Path("test.pdf").unlink()  # noqa: S108
