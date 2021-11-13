import nox


@nox.session
def docs(session):
    """Rebuild and deploy sphinx documentation to gh-pages branch"""
    session.install(".[docs]")
    session.cd("docs")
    session.run("make", "clean")
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
    * Run interrogate
    """
    session.install(".[lint]")
    session.run("black", "fredapi", "fredapi/tests")
    session.run("isort", "fredapi", "fredapi/tests")
    session.run("flake8", "fredapi", "fredapi/tests")
    session.run("interrogate", "fredapi", "fredapi/tests")


@nox.session
def test_coverage(session):
    """Generate test coverage statistics"""
    session.install(".[test]")
    session.run(
        "coverage",
        "run",
        "--source" "fredapi.fred" "fredapi/tests/test_fred.py",
    )
