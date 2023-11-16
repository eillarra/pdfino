============
Integrations
============

Django
------

PDFino includes a Django response that can be used directly in a view:

.. code-block:: python

  from pdfino import Document
  from pdfino.django import PdfResponse


  def my_view(request):
      doc = Document()
      doc.h1('Django PDF')
      return PdfResponse(doc.bytes, filename='django.pdf')

The :class:`pdfino.django.PdfResponse` class is a subclass of Django's ``HttpResponse`` so, of course, it will only
work if you have Django installed in your project.
