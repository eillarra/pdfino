Changelog
=========

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- Template margins and pagesize not being applied to the document when using the `template` attribute.

### Added
- Columns to `Template` class (defaults to one column).
- Markdown helper for adding complex lists.
- Title and author for `Document` class.
- Outline using headings.
- Extra documentation about styles.

### Changed
- Default font size and leading for paragraphs and headings.
- Hyphenate long words in paragraphs (default is False): needs `pyphen` package.
- Docstring format, using Sphinx style.
- Keep separator elements together.

### Removed
- `bu` style (bullet). Use `ul` instead.

## [0.1.0] - 2023-11-16

### Added
- Basic structure of the project. Minimum viable product.
- `Template` and `Document` classes.
- Shortcut methods to add elements to the document: p, h1, h2, h3, h4, hr, ul, ol
- Sample stylesheet.
- Custom styles via `styles` and `options` parameter.
- Initial documentation.

## [0.0.1] - 2023-11-10

- Just a placeholder to reserve the name on PyPI.


[unreleased]: https://github.com/eillarra/pdfino/compare/0.1.0...HEAD
[0.1.0]: https://github.com/eillarra/pdfino/releases/tag/0.1.0
[0.0.1]: https://github.com/eillarra/pdfino/releases/tag/0.0.1
