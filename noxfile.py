import nox


@nox.session
def docs(session):
    """Rebuild and deploy sphinx documentation to gh-pages branch"""
    session.install(".[docs]")
    session.cd("docs")
    session.run("make", "gh-deploy")


@nox.session
def interrorgate(session):
    """Run interrogate and create fresh interrogate badge for README"""
    session.install(".[lint]")
    session.run("interrogate", "--generate-badge", "docs/_static/", "fredapi")


@nox.session
def lint(session):
    """Apply linting standards

    * Run black formatting
    * Run isort
    * Run flake8
    """
    session.install(".[lint]")
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
    session.install(".[lint]")
    session.run("black", "tests")
    session.run("isort", "tests")
    session.run("flake8", "tests")
