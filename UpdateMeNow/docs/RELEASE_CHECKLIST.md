# UpdateMeNow v1 Release Checklist

Use this checklist before tagging a v1 release.

## Required Checks

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
python -m compileall -q src tests
umn --version
umn sources list
umn config init
umn config validate
umn sources test --timeout 20
umn scan --hours 6 --export excel,json
```

## Acceptance Criteria

- `umn scan` defaults to the last 6 hours.
- Bare `umn` runs the default scan.
- `umn --version` reports the package version from `pyproject.toml`.
- `umn`, `umn scan`, and `umn sources list` work from folders without local
  `config/` files by using packaged defaults.
- `umn config validate` validates local editable config after `umn config init`.
- Excel export is created in `reports/` by default.
- JSON export works with `--export json` and `--export excel,json`.
- Reports use only configured RSS feeds and official public APIs.
- No scraping, browser automation, paid APIs, database, dashboard, scheduling, alerting, or AI summaries are added.
- Tests pass locally before release.

## Manual Report Review

- Open the latest Excel file in `reports/`.
- Confirm it has one `Cyber Updates` worksheet.
- Confirm headers are bold, the top row is frozen, filters are enabled, URLs are clickable, and rows are grouped by source.
- Confirm the latest JSON file includes `scan`, `sources`, and `items`.
- Review `CHANGELOG.md` before tagging a release.
