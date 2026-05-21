# UpdateMeNow

UpdateMeNow is a Python 3.11+ command-line tool for collecting recent cybersecurity updates from free public RSS feeds and official public APIs, then turning them into a clean Excel report.

The tool exists for one practical reason: a technical user should be able to run one command, get a reliable snapshot of current cyber advisories and vulnerability news, and not have to manually chase feeds, websites, or spreadsheets.

This public release is intentionally simple:

- one CLI entry point: `umn`
- one default action: `umn scan`
- one default export: Excel
- one default time window: last 6 hours
- no scraping, no database, no dashboard, no AI summaries

## Why This Project Exists

Security information is scattered across many sources:

- government advisories
- vulnerability trackers
- vendor security blogs
- threat research feeds
- security news outlets

UpdateMeNow consolidates those signals into a single report so you can:

- spot what changed recently
- filter by source, keyword, or vendor
- see CVEs and matches at a glance
- keep a local archive of scans

The goal is usefulness without complexity. It is a reporting tool, not a threat platform.

## Project Scope

### What v1 does

- scans configured RSS feeds and official public APIs
- defaults to the last 6 hours
- exports Excel by default
- supports JSON export
- groups items by source order
- sorts newest to oldest within each source
- detects CVEs, keywords, vendors/products, and broad categories
- removes obvious duplicates

### What v1 does not do

- no web scraping
- no browser automation
- no paid APIs
- no database
- no dashboard
- no scheduling
- no alerting
- no AI-generated summaries
- no exploitation, phishing, malware, or offensive automation support

## CLI Overview

The command line structure is:

```bash
umn
├── scan
├── config init
├── config validate
├── sources list
└── sources test
```

### Default command

Running `umn` with no arguments is the same as:

```bash
umn scan
```

And `umn scan` defaults to:

```bash
umn scan --hours 6 --export excel
```

If you only remember one thing, remember this:

```bash
umn
```

That runs the default scan for the last 6 hours and exports Excel.

## Main Commands

### `umn scan`

Collect updates, process them, dedupe them, and export a report.

Common options:

```bash
umn scan --hours 24
umn scan --days 7
umn scan --source nvd
umn scan --source cisa_kev --source github
umn scan --keyword ransomware
umn scan --export excel,json
umn scan --dedupe strict
umn scan --dedupe normal
umn scan --dedupe relaxed
```

### `umn config init`

Create local editable configuration files.

```bash
umn config init
umn config init --force
```

### `umn config validate`

Validate configuration files before scanning.

```bash
umn config validate
```

### `umn sources list`

Show the configured sources, their groups, types, and enablement status.

```bash
umn sources list
```

### `umn sources test`

Check whether sources are reachable.

```bash
umn sources test
umn sources test --all
umn sources test --timeout 20
```

## Install and Run

If you are new to Python or command-line tools, use the section for your operating system below.

### Mac

1. Open Terminal.
2. Go to the project folder:
   ```bash
   cd /path/to/UpdateMeNow
   ```
3. Create a virtual environment:
   ```bash
   python3.11 -m venv .venv
   ```
4. Activate it:
   ```bash
   source .venv/bin/activate
   ```
5. Install the project:
   ```bash
   python -m pip install -e ".[dev]"
   ```
6. Run the tool:
   ```bash
   umn
   ```

### Linux

1. Open your terminal.
2. Go to the project folder:
   ```bash
   cd /path/to/UpdateMeNow
   ```
3. Create a virtual environment:
   ```bash
   python3.11 -m venv .venv
   ```
4. Activate it:
   ```bash
   source .venv/bin/activate
   ```
5. Install the project:
   ```bash
   python -m pip install -e ".[dev]"
   ```
6. Run the tool:
   ```bash
   umn
   ```

### Windows

1. Open PowerShell.
2. Go to the project folder:
   ```powershell
   cd C:\path\to\UpdateMeNow
   ```
3. Create a virtual environment:
   ```powershell
   py -3.11 -m venv .venv
   ```
4. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
5. Install the project:
   ```powershell
   python -m pip install -e ".[dev]"
   ```
6. Run the tool:
   ```powershell
   umn
   ```

## Configuration

Default editable config files live in `config/`:

- `config/sources.yaml`
- `config/keywords.yaml`

Package defaults live in `src/updatemenow/defaults/` and are copied into your local config with `umn config init`.

The default source catalog focuses on high-signal, low-noise sources and keeps optional feeds disabled until you enable them manually.

## Report Output

By default, scans write an Excel workbook into `reports/`:

```bash
reports/UpdateMeNow_Report_2026-05-20_6h.xlsx
```

The workbook is designed to be readable and useful:

- one worksheet named `Cyber Updates`
- bold header row
- frozen top row
- filters enabled
- clickable URLs
- CVE, keyword, vendor, category, and age fields
- source-group styling and table formatting

JSON export is also available:

```bash
umn scan --export json
umn scan --export excel,json
```

## Duplicate Handling

Duplicate handling is configurable with `--dedupe`:

```bash
umn scan --dedupe strict
umn scan --dedupe normal
umn scan --dedupe relaxed
```

- `strict` keeps only same-URL and same-source title duplicates.
- `normal` also removes same-title items within the same source group.
- `relaxed` can collapse obvious cross-feed near-duplicates when the title, CVE, vendor, and timing signals line up.

## Development And Testing

Run these checks before changing behavior:

```bash
python -m pytest
umn config validate
```

Release-readiness guidance lives in:

- `docs/RELEASE_CHECKLIST.md`
- `CHANGELOG.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/PUBLIC_RELEASE.md`

## Safety

UpdateMeNow is for defensive and educational reporting only. It does not provide offensive capability, scraping, or support for abuse.

Use configured public sources respectfully, and avoid overloading websites or ignoring source terms.

## Roadmap

- Milestone 1: project foundation
- Milestone 2: config commands
- Milestone 3: source commands
- Milestone 4: collectors
- Milestone 5: processing pipeline
- Milestone 6: exports
- Milestone 7: polish and release readiness

## License

MIT. See `LICENSE`.
