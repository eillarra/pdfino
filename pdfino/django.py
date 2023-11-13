"""Module for Django PDF response class."""

try:
    from django.http import HttpResponse  # type: ignore
except ImportError as exc:
    raise ImportError("Django is required for the PdfResponse class") from exc


class PdfResponse(HttpResponse):
    """A Django HttpResponse that returns PDF content."""

    def __init__(self, content: bytes, *, filename: str, as_attachment: bool = False, **kwargs):
        """Create a PDF response."""
        self.filename = filename
        self.as_attachment = as_attachment
        kwargs.setdefault("content_type", "application/pdf")
        super().__init__(content, **kwargs)
