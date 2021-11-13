import nox


@nox.session
def docs(session):
    """Rebuild and deploy sphinx documentation to gh-pages branch"""
    session.install(".[docs]")
    # Run interrogate to create fresh interrorgate badge for docs
    session.run("interrogate", "--generate-badge", "docs/_static/", "fredapi")
    session.run("docs/make", "gh-deploy")


@nox.session
def lint(session):
    """Apply linting standards

    * Run black formatting
    * Run isort
    * Run flake8
    """
    session.install("black", "isort", "flake8")
    session.run("black", "fredapi")
    session.run("isort", "fredapi")
    session.run("flake8", "fredapi")


@nox.session
def lint_tests(session):
    """Apply linting standards to the test files

    * Run black formatting
    * Run isort
    * Run flake8
    """
    session.install("black", "isort", "flake8")
    session.run("black", "tests")
    session.run("isort", "tests")
    session.run("flake8", "tests")
