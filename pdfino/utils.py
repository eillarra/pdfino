"""Utility functions for PDFino."""

from .type_definitions import ElementOptions, Margins


def get_margins(options: ElementOptions) -> Margins:
    """Get margins from the options of an element.

    :param options: Options for an element.
    :return: Margins tuple.
    """
    if "margins" in options:
        try:
            return Margins(*options["margins"])
        except TypeError as exc:
            raise TypeError("Invalid margins value. `margins` should be a tuple of 4 integers.") from exc

    return Margins(
        top=options.get("margin_top", 0),
        right=options.get("margin_right", 0),
        bottom=options.get("margin_bottom", 0),
        left=options.get("margin_left", 0),
    )
