import nox


@nox.session
def docs(session):
    """Rebuild and deploy sphinx documentation to gh-pages branch"""
    session.install(".[docs]")
    session.run(["make", "gh-deploy"])
