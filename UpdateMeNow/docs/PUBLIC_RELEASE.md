# Public Release Checklist

Use `UPLOADTHIS/UpdateMeNow` as the GitHub-ready release folder.

## Recommended publish folder

- `/Users/abbasn/Projects/UpdateMeNow/UPLOADTHIS/UpdateMeNow`

Upload the contents of that folder to GitHub. Do not upload the parent working
folders, virtual environments, report outputs, caches, or old staging folders.

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
   - no `.DS_Store`

## What makes this folder public-ready

- Source code and tests are included.
- Local-only runtime artifacts are excluded.
- Runtime commands use packaged default config when local config files do not
  exist.
- Documentation is present at the top level and in `docs/`.
- The project name remains `UpdateMeNow`.
