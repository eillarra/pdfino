PDFINO
======

[![github-tests-badge]][github-tests]
[![github-mypy-badge]][github-mypy]
[![codecov-badge]][codecov]
[![pypi-badge]][pypi]
[![pypi-versions]][pypi]
[![license-badge]](LICENSE)


Welcome to PDFINO (/pəˈdɪfino/), a nimble wrapper around [ReportLab][reportlab] designed to simplify PDF document
creation. It offers an opinionated yet straightforward API for creating templates and documents. Easily define styles
for templates without the complexity of multiple ReportLab styles. PDFINO dynamically generates and applies styles
to document elements based on provided options, making the process more intuitive.

### Getting started 🌯

```python
from pdfino import Document

doc = Document()
doc.h1("Hello World", options={"color": "blue", "margin_bottom": 30})
doc.p("Generate PDFs effortlessly with PDFINO.")
doc.hr(height=2, options={"color": "#ffa500", "margins": (30, 100, 0, 100)})
data = doc.bytes
```

**Remember:** PDFINO keeps things streamlined, but it won't replace all of ReportLab's powers.
If you want more control, easily blend ReportLab flowables:

```python
from pdfino import Document
from reportlab.platypus import Paragraph

doc = Document()
doc.add(Paragraph("Hello World", doc.styles["h1"]))
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
