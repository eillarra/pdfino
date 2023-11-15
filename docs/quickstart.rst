==========
Quickstart
==========

Installation
------------

.. code-block:: bash

  $ pip install pdfino

Create your first PDF
---------------------

Using PDFino is very simple. Just create a new ``Document`` and start adding content to it. If you want to
tweak the styles of the document, you can always use custom templates and styles (see :ref:`templates`).

.. code-block:: python

  from pdfino import Document


  doc = Document()
  doc.h1('Hello World!')
  doc.p('PDFino is a simple PDF generator.')
  doc.save_as('hello_world.pdf')
