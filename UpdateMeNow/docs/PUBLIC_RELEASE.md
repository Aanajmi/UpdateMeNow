# Public Release Checklist

Use this copy as the GitHub-ready release folder.

## Recommended publish folder

- `public/UpdateMeNow`

## Before publishing

1. Review `README.md` for accuracy.
2. Review `docs/PRD.md` for scope alignment.
3. Run the test suite locally if you are keeping a working environment:
   ```bash
   python -m pytest
   ```
4. Confirm the package metadata in `pyproject.toml`.
5. Keep the repo root clean:
   - no `.venv/`
   - no `reports/`
   - no `.pytest_cache/`
   - no `__pycache__/`

## What makes this folder public-ready

- Source code and tests are included.
- Local-only runtime artifacts are excluded.
- Documentation is present at the top level and in `docs/`.
- The project name remains `UpdateMeNow`.

