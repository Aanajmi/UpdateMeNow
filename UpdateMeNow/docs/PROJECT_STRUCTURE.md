# Project Structure

This document explains the public release copy of UpdateMeNow.

## Root Files

- `README.md` — main project overview, install steps, and usage examples.
- `CHANGELOG.md` — release notes and version history.
- `CONTRIBUTING.md` — contribution guidelines for future collaborators.
- `SECURITY.md` — security contact and reporting guidance.
- `LICENSE` — MIT license text.
- `pyproject.toml` — project metadata, dependencies, and CLI entry point.
- `.gitignore` — files and folders excluded from version control.

## Application Code

- `src/updatemenow/` — the Python package for the CLI application.
  - `cli.py` — Typer command-line interface and user commands.
  - `pipeline.py` — scan orchestration, filtering, deduping, and export flow.
  - `dedupe.py` — duplicate detection and canonicalization logic.
  - `config.py` — config loading, validation, and initialization.
  - `filters.py` — time and keyword filtering helpers.
  - `models.py` — Pydantic data models and enums.
  - `text_detection.py` — CVE, vendor, keyword, and category detection helpers.
  - `exporters/` — Excel and JSON report generation.
  - `sources/` — RSS/API source collectors and source health checks.

## Configuration

- `config/sources.yaml` — default source catalog.
- `config/keywords.yaml` — default keyword and vendor watchlists.

## Documentation

- `docs/PRD.md` — product requirements source of truth.
- `docs/RELEASE_CHECKLIST.md` — release-readiness checklist.
- `docs/PROJECT_STRUCTURE.md` — this file.
- `docs/PUBLIC_RELEASE.md` — publishing checklist for GitHub.

## Tests

- `tests/` — automated test suite.
  - `test_cli.py` — CLI behavior.
  - `test_config*.py` — configuration behavior.
  - `test_exporters.py` — report export behavior.
  - `test_pipeline.py` — scan pipeline behavior.
  - `test_processing.py` — dedupe, filtering, and text processing.
  - `test_sources*.py` — source commands and health checks.
  - `test_text_detection.py` — CVE, vendor, and category detection.
  - `test_package_metadata.py` — version and packaging checks.

