#!/usr/bin/env python
from setuptools import setup

# Fetch the version number from fredapi.version
temporary_globals = {}  # type: ignore
with open("fredapi/_version.py") as fp:
    exec(fp.read(), temporary_globals)
version_str = temporary_globals["__version__"]

install_requires = ["pandas"]
docs_requires = [
    "nbsphinx",
    "myst-parser",
    "sphinx",
    "sphinxcontrib.napoleon",
    "sphinx_rtd_theme",
    "ipython",
    "interrogate",
]
test_requires = ["pytest"]
dev_requires = (
    ["black", "mypy", "flake8", "bump2version", "pre-commit", "nox", "isort"]
    + docs_requires
    + test_requires
)

LONG_DESCRIPTION = open("DESCRIPTION.rst").read()

setup(
    name="fredapi",
    version=version_str,
    url="https://github.com/mortada/fredapi",
    author="Mortada Mehyar",
    # author_email='',
    description="Python API for Federal Reserve Economic Data (FRED) from St. Louis Fed",
    long_description=LONG_DESCRIPTION,
    test_suite="fredapi.tests.test_fred",
    packages=["fredapi"],
    platforms=["Any"],
    install_requires=install_requires,
    extras_require={"docs": docs_requires, "tests": test_requires, "dev": dev_requires},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
