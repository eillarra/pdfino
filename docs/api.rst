=============
API reference
=============


Main classes
------------

.. autoclass:: pdfino.Template
  :members:
  :member-order: bysource

.. autoclass:: pdfino.Document
  :members:
  :member-order: bysource
  :exclude-members: actual_width, template_class

Custom types
------------

.. autoclass:: pdfino.Font
  :show-inheritance:

.. autoclass:: pdfino.Margins
  :show-inheritance:

.. autoclass:: pdfino.Pagesize
  :special-members: from_name

.. autoclass:: pdfino.Style
  :show-inheritance:

.. autoclass:: pdfino.type_definitions.LayoutOptions
  :members:
  :undoc-members:
  :show-inheritance:

.. autoclass:: pdfino.type_definitions.StyleOptions
  :members:
  :undoc-members:
  :show-inheritance:

.. autoclass:: pdfino.type_definitions.ElementOptions
  :members:
  :undoc-members:
  :show-inheritance:

Integrations
------------

.. autoclass:: pdfino.django.PdfResponse
