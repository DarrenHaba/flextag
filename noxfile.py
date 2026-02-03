"""Nox sessions for local multi-Python-version testing.

Usage (via poetry):
    poetry run python -m nox                          Run tests on all Python versions
    poetry run python -m nox -s "tests-3.12"          Run tests on a specific version
    poetry run python -m nox -s lint                  Run linting (black + flake8)
    poetry run python -m nox -l                       List available sessions

Usage (if nox is installed globally):
    nox                          Run tests on all Python versions
    nox -s "tests-3.12"         Run tests on a specific version
    nox -s lint                  Run linting
    nox -l                       List available sessions

Requires:
    - Python versions installed and accessible via `py -3.X` (Windows) or `pythonX.Y` (Unix)

On Windows, nox uses the `py` launcher to find Python versions automatically.
"""

import nox

# Python versions that match pyproject.toml: python = ">=3.10,<3.14"
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run the test suite against a specific Python version."""
    # Install the package and its dependencies
    session.run("pip", "install", ".", silent=True)
    session.install("pytest", "pytest-cov")
    # ftml is an optional dependency used by some tests
    session.install("ftml", silent=True)

    # Run tests
    session.run(
        "pytest",
        "--tb=short",
        "-v",
        *session.posargs,
    )


@nox.session(python="3.12")
def lint(session):
    """Run linting checks (black + flake8)."""
    session.install("black", "flake8", "flake8-docstrings")

    session.run("black", "--check", "src/", "tests/")
    session.run("flake8", "src/", "tests/", "--max-line-length=88")
