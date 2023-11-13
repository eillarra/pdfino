"""Test the pdfino.utils module."""

import pytest

from pdfino.utils import get_margins


@pytest.mark.parametrize(
    "options, expected",
    [
        ({"margins": (10, 20, 30, 40)}, (10, 20, 30, 40)),
        ({"margin_top": 10, "margin_right": 20, "margin_bottom": 30, "margin_left": 40}, (10, 20, 30, 40)),
        ({"margin_top": 10, "margin_left": 20}, (10, 0, 0, 20)),
    ],
)
def test_get_margins(options, expected):
    """Test get_margins function."""
    assert get_margins(options) == expected


@pytest.mark.parametrize(
    "invalid_value",
    [
        "invalid",
        123,
        [10, 20],
        {"top": 10, "right": 20},
    ],
)
def test_get_margins_with_invalid_value(invalid_value):
    """Test get_margins function with invalid value."""
    options = {"margins": invalid_value}
    with pytest.raises(TypeError) as exc_info:
        get_margins(options)
    assert str(exc_info.value) == "Invalid margins value. `margins` should be a tuple of 4 integers."
