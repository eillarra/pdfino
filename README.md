PDFino
======

[![github-tests-badge]][github-tests]
[![github-mypy-badge]][github-mypy]
[![codecov-badge]][codecov]
[![pypi-badge]][pypi]
[![pypi-versions]][pypi]
[![license-badge]](LICENSE)


PDFino (/pəˈdɪfino/) is a Python library for generating PDF files. It is built on top of [ReportLab][reportlab],
a powerful PDF generation library for Python. PDFino is designed to be simple and easy to use.
It provides a high-level API for generating PDF files without having to deal with the low-level details of ReportLab.

### Getting started 🌯

```python
from pdfino import Document


doc = Document()
doc.h1("Hello World", options={"color": "blue", "margin_bottom": 30})
doc.p("Generate PDFs effortlessly with PDFino.")
doc.hr(height=2, options={"color": "#ffa500", "margins": (30, 100, 0, 100)})
data = doc.bytes
```

PDFino keeps things streamlined, but **it won't replace all of ReportLab's powers**. You can always add ReportLab
flowables directly to your document if you need to.

```python
from pdfino import Document
from reportlab.platypus import Paragraph


doc = Document()
doc.add(Paragraph("Hello World", doc.stylesheet["h1"]))
doc.save_as("hello_world.pdf")
```

For detailed usage, check out [pdfino.readthedocs.io][readthedocs].

### Run the tests 🧪

```bash
poetry run pytest --cov=pdfino --cov-report=term
```

### Style guide 📖

Tab size is 4 spaces. Keep lines under 120 characters. Feeling iffy? Run `ruff` before you commit:

```bash
poetry run ruff format . && poetry run ruff check pdfino
```


[codecov]: https://codecov.io/gh/eillarra/pdfino
[codecov-badge]: https://codecov.io/gh/eillarra/pdfino/graph/badge.svg?token=w93ZuZTpkW
[github-mypy]: https://github.com/eillarra/pdfino/actions?query=workflow%3Amypy
[github-mypy-badge]: https://github.com/eillarra/pdfino/workflows/mypy/badge.svg
[github-tests]: https://github.com/eillarra/pdfino/actions?query=workflow%3Atests
[github-tests-badge]: https://github.com/eillarra/pdfino/workflows/tests/badge.svg
[license-badge]: https://img.shields.io/badge/license-MIT-blue.svg
[pypi]: https://pypi.org/project/pdfino/
[pypi-badge]: https://badge.fury.io/py/pdfino.svg
[pypi-versions]: https://img.shields.io/pypi/pyversions/pdfino.svg
[readthedocs]: https://pdfino.readthedocs.io/en/latest/

[reportlab]: https://www.reportlab.com/opensource/
