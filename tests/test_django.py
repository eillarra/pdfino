"""Test the pdfino.django module."""

from django.http import HttpResponse

from pdfino import Document
from pdfino.django import PdfResponse


def test_pdf_response():
    """Test the PdfResponse class."""
    with Document() as doc:
        doc.p("Test paragraph")
        data = doc.bytes

    pdf_response = PdfResponse(data, filename="test.pdf", as_attachment=True)
    assert pdf_response.as_attachment
    assert pdf_response.filename == "test.pdf"
    assert isinstance(pdf_response, HttpResponse)
    assert pdf_response.content == data
