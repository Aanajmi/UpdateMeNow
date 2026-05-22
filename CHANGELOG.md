# Changelog

## 1.0.0 - 2026-05-21

Initial v1 release candidate.

- Adds the `umn` CLI with bare `umn` and `umn scan` default scan behavior.
- Scans the last 6 hours by default.
- Collects from configured RSS feeds and official public APIs only.
- Supports CISA KEV, NVD, GitHub Security Advisories, RSS feeds, and an expanded optional source catalog.
- Detects CVEs, configured keywords, vendors/products, and simple categories.
- Removes obvious duplicates by canonical URL and same normalized title within the same source.
- Exports Excel reports by default and supports JSON export.
- Includes config initialization, config validation, source listing, and source reachability checks.
- Uses packaged default config for runtime commands when local `config/` files do not exist.
