# Changelog

## Version 0.4.4

## Added

* Improved documentation
    * Move README documentation into [sphinx](https://www.sphinx-doc.org/en/master/) docs
    * Host the sphinx documentation on [gh-pages](https://pages.github.com) branch
    * Add [shied.io](https://shields.io) badges to README
    * Introduce Changelog
    * Add brief contribution guide
* Added linting suite
    * [black formatting](https://black.readthedocs.io/en/stable/)
    * [flake8](https://flake8.pycqa.org/en/latest/)
    * [isort](https://github.com/PyCQA/isort)
    * [interrogate](https://interrogate.readthedocs.io/en/latest/)
    * [pre-commit](https://pre-commit.com)
* Introduce [Nox](https://nox.thea.codes/en/stable/) to build and deploy docs and apply linting
* GitHub issue templates for bugs and feature requests

## Changed

* Updated `setup.py` to incorporate package installs for documentation, tests, and development
* Small refactor to how `setup.py` sources version number from `_version.py`
* Converted string formatting to [f-strings](https://realpython.com/python-f-strings/)
