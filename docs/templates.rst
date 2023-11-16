.. _templates:

================
Custom templates
================

You can extend the default :class:`pdfino.Template` and :class:`pdfino.Document` classes to personalize your PDFs.
For example, you can add custom fonts and styles, change the page size, etc. to a template.

.. tabs::

  .. tab:: Template as parameter

    A template instance can be passed as an argument to the :class:`pdfino.Document` class constructor:

    .. code-block:: python

      from pathlib import Path

      from pdfino import Template, Document, Pagesize, Font


      class RobotTemplate(Template):
          """A template with some custom parameters and styles."""

          pagesize = Pagesize.from_name("Letter")
          fonts = [
              Font("Roboto", default=True, normal=Path("Roboto-Regular.ttf"), bold=Path("Roboto-Bold.ttf"))
          ]


      doc = Document(template=RobotTemplate())
      doc.h1("Hello robots!")
      doc.save_as("hello.pdf")

  .. tab:: Reusable custom document

    If you plan to reuse the same template in multiple documents, you can also subclass :class:`pdfino.Document`
    and set the ``template_class`` class attribute:

    .. code-block:: python

      from pdfino import Document

      from .templates import RobotTemplate


      class RobotDocument(Document):
          """A document using a custom template."""

          template_class = RobotTemplate


      doc = RobotDocument()
      doc.h1("Hello robots!")
      doc.save_as("hello.pdf")

.. note::

  The ``template`` init argument has priority over the ``template_class`` class attribute if both are specified
  for a document.

Default styles
--------------

Styles are something that require some tweaking in ReportLab. In PDFino, some styles are created by default for you
and you have a simple API to add new ones or modify the existing ones. You can also use the ``options`` argument
to change the style of a single element without having to create new styles.

The :func:`pdfino.styles.get_sample_stylesheet` function returns the collection of styles that are created by default
for a :class:`pdfino.Template`. The default styles are:

- ``h1``: a very large, bold title
- ``h2``: a large, bold subtitle
- ``h3``: a medium, bold subtitle
- ``h4``: a normal, bold subtitle
- ``p``: a normal paragraph

.. note::

  These styles allow you to use the shortcut API to add titles and paragraphs to your document:

  .. code-block:: python

    doc = Document()
    doc.h1("Hello world!")
    doc.h3("This is a subtitle.")
    doc.p("This is a paragraph.")

  You can start with a clean stylesheet if you use the ``use_sample_stylesheet = False`` class attribute in
  your custom template class, but then you will have to create your own default styles if you want to use the
  shortcut API. The shortcut API just calls the :meth:`pdfino.Document.add_paragraph` method with the corresponding
  style name, so if you don't want to use the default styles you can always call that method directly.

Custom styles
-------------

You can update existing styles or add new styles to your stylesheet by adding a ``styles`` class attribute
(a list of :class:`pdfino.Style`) to your custom template or document.

.. code-block:: python

  from pathlib import Path

  from pdfino import Document, Font, Pagesize, Style, Template


  class MyTemplate(Template):
      use_sample_stylesheet = False
      pagesize = Pagesize.from_name("A5")
      fonts = [
          Font("Roboto Slab", normal=Path("Roboto-Slab.ttf")),
          Font("Roboto", default=True, normal=Path("Roboto-Thin.ttf"), bold=Path("Roboto-Regular.ttf")),
      ]
      styles = [
          Style("h1", font_name="Roboto Slab", font_size=20),
          Style("p", font_size=10, options={"align": "justify"}),
      ]


  class MyDocument(Document):
      template_class = MyTemplate
      styles = [Style("note", parent="p", font_size=8, options={"color": "blue"})]

      def note(self, text):
          self.add_paragraph(text, style="note")


  doc = MyDocument()
  doc.h1("Hello world! In Roboto Slab!")
  doc.p("This is a justified paragraph, defined in the template.")
  doc.note("This is my special paragraph for notes. I even created a method for it!")
  doc.p("This is another paragraph, with centered text.", options={"align": "center"})
  doc.save_as("my_hello.pdf")
