PDFINO
======

[![github-tests-badge]][github-tests]
[![github-mypy-badge]][github-mypy]
[![codecov-badge]][codecov]
[![pypi-badge]][pypi]
[![pypi-versions]][pypi]
[![license-badge]](LICENSE)


PDFINO (/pəˈdɪfino/) is a thin wrapper around [ReportLab][reportlab] that makes it easier to create PDF documents.
It is an opinionated library that provides a simple API to create templates and documents. Styles are easy to define
for a template and instead of having to deal with multiple ReportLab styles, PDFINO can create styles on the fly
and apply them to the document elements based on the options passed to the different methods.

**PDFINO doesn't try to be a full featured PDF library.** It is just a thin wrapper around ReportLab. If you need
more control over the document, you can always add ReportLab elements directly to it.

### Basic usage

```python
from pdfino import Document

with Document() as doc:
    doc.h1("Hello World", options={"color": "blue", "margin_bottom": 30})
    doc.p("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore...")
    doc.hr(height=2, options={"color": "#ffa500", "margins": (30, 100, 0, 100)})
    doc.save_as("hello_world.pdf")
```

Complete documentation can be found at [pdfino.readthedocs.io][readthedocs].

### Run the tests

```bash
poetry run pytest --cov=pdfino --cov-report=term
```

### Style guide

Tab size is 4 spaces. Max line length is 120. You should run `ruff` before committing any change.

```bash
poetry run ruff format . && poetry run ruff check pdfino
```


[codecov]: https://codecov.io/gh/eillarra/pdfino
[codecov-badge]: https://codecov.io/gh/eillarra/pdfino/branch/master/graph/badge.svg
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
