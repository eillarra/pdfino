"""Test the pdfino.type_definitions module."""

import pytest
from reportlab.lib import pagesizes

from pdfino.type_definitions import Pagesize


@pytest.mark.parametrize(
    "name, expected",
    [
        ("A4", pagesizes.A4),
        ("LETTER", pagesizes.LETTER),
        ("letter", pagesizes.LETTER),
    ],
)
def test_pagesize_from_name(name, expected):
    """Test get_margins function."""
    assert Pagesize.from_name(name) == expected


@pytest.mark.parametrize(
    "invalid_name",
    [
        "invalid",
        123,
        [10, 20],
        {"top": 10, "right": 20},
    ],
)
def test_pagesize_from_name_with_invalid_name(invalid_name):
    """Test get_margins function with invalid value."""
    with pytest.raises(ValueError) as exc_info:
        Pagesize.from_name(invalid_name)
    assert str(exc_info.value) == f"Invalid pagesize: {invalid_name}"
