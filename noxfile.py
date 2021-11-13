import nox


@nox.session
def docs(session):
    """Rebuild and deploy sphinx documentation to gh-pages branch"""
    session.install(".[docs]")
    session.run(["make", "gh-deploy"])


@nox.session
def lint(session):
    """Apply black formatting"""
    session.install("black")
    session.run("black", "fredapi")
    session.run("black", "tests")
