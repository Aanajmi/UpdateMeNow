# Contributing

Thanks for helping improve UpdateMeNow.

## Development Setup

Use Python 3.11+ and a local virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Project Rules

- Keep v1 simple and reliable.
- Use RSS feeds and official public APIs only.
- Do not add scraping.
- Do not add a database.
- Do not add a dashboard.
- Do not add AI summaries.
- Write focused tests as features are added.

## Tests

```bash
python -m pytest
```
