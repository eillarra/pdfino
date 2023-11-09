PDFINO
======

[![github-tests-badge]][github-tests]
[![github-mypy-badge]][github-mypy]
[![codecov-badge]][codecov]
[![pypi-badge]][pypi]
[![pypi-versions]][pypi]
[![license-badge]](LICENSE)


### Basic usage

```python
from pdfino import Document

pdf = Document()
pdf.h1("This is a heading")
pdf.p("Hello world!", align="center", classes=["mb-md"])
pdf.p("This is a paragraph.", classes=["mb-md"])
pdf.p("This is another paragraph.", classes=["mb-md"])
pdf.get_django_response("hello.pdf")
```

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
