from pathlib import Path
import tomllib

from updatemenow import __version__


PYPROJECT = Path("pyproject.toml")
CHANGELOG = Path("CHANGELOG.md")
REQUIRED_RUNTIME_DEPENDENCIES = [
    "typer",
    "rich",
    "feedparser",
    "httpx",
    "pydantic",
    "PyYAML",
    "openpyxl",
]


def test_package_version_matches_project_metadata() -> None:
    project = _project_metadata()

    assert project["version"] == __version__


def test_cli_entry_point_is_umn() -> None:
    project = _project_metadata()

    assert project["scripts"]["umn"] == "updatemenow.cli:main"


def test_required_runtime_dependencies_are_declared() -> None:
    dependencies = _project_metadata()["dependencies"]

    for dependency in REQUIRED_RUNTIME_DEPENDENCIES:
        assert any(value.startswith(dependency) for value in dependencies)


def test_changelog_contains_current_version() -> None:
    changelog = CHANGELOG.read_text(encoding="utf-8")

    assert f"## {__version__} - Unreleased" in changelog


def _project_metadata() -> dict:
    pyproject = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return pyproject["project"]
