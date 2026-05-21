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
If you want `umn` to stay available after reboot and work from any folder, use `pipx`.

### Install `pipx` once

You only need to do this one time.

#### Mac

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Close Terminal and reopen it after `ensurepath`.

#### Linux

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Close and reopen your terminal after `ensurepath`.

#### Windows

In PowerShell:

```powershell
py -3.11 -m pip install --user pipx
py -3.11 -m pipx ensurepath
```

Close and reopen PowerShell after `ensurepath`.

### Install UpdateMeNow with `pipx`

#### Mac

```bash
pipx install /path/to/UpdateMeNow
```

#### Linux

```bash
pipx install /path/to/UpdateMeNow
```

#### Windows

```powershell
pipx install C:\path\to\UpdateMeNow
```

### Run it from anywhere

After installation, you can run:

```bash
umn --version
umn
```

`umn` and `umn scan` work from any folder. If local files do not exist at
`config/sources.yaml` and `config/keywords.yaml`, UpdateMeNow uses the packaged
default config included with the app.

Only create local config files when you want to edit sources or keywords:

```bash
umn config init
```

### Update later

If you change the project and want the installed version refreshed:

```bash
pipx install --force /path/to/UpdateMeNow
```

## Troubleshooting

### `Config is invalid` and says config files are missing

Bare `umn`, `umn scan`, and `umn sources list` should not fail just because
you are running from a folder without `config/`. They fall back to packaged
defaults.

`umn config validate` is different: it checks local editable config files.
If you want local files to validate or customize, run:

```bash
umn config init
umn config validate
```

If you installed an older local copy with `pipx`, reinstall from the updated
project folder:

```bash
pipx install --force /path/to/UpdateMeNow
```

### `umn` is not found

- Close and reopen your terminal after `pipx ensurepath`.
- Run:
  ```bash
  pipx ensurepath
  ```
- Confirm `pipx` is installed:
  ```bash
  pipx --version
  ```

### `pipx` is not found

- Make sure Python 3.11 or newer is installed.
- Run:
  ```bash
  python3 --version
  ```
- Reinstall `pipx`:
  ```bash
  python3 -m pip install --user pipx
  python3 -m pipx ensurepath
  ```

### PowerShell blocks activation

- Run PowerShell as a normal user first.
- If you use the developer setup, activate with:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- If PowerShell blocks scripts, you may need to adjust your execution policy for your user account.

### Install path is wrong

- Replace `/path/to/UpdateMeNow` or `C:\path\to\UpdateMeNow` with the actual folder path on your computer.
- If you are using the public release copy, the folder name is `UpdateMeNow`.

### Developer setup

If you are contributing to the project and want a local editable setup instead of `pipx`, use this:

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

The same editable setup works for Linux and Windows if you prefer development mode over `pipx`.

## Configuration

Packaged default config files live in `src/updatemenow/defaults/` and are used
automatically by runtime commands when no local config exists.

Editable local config files live in `config/` after you run `umn config init`:

- `config/sources.yaml`
- `config/keywords.yaml`

`umn config init` copies the packaged defaults into `config/` so you can change
sources and watchlists without editing package code.

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


## Safety

UpdateMeNow is for defensive and educational reporting only. It does not provide offensive capability, scraping, or support for abuse.

Use configured public sources respectfully, and avoid overloading websites or ignoring source terms.



## License

MIT. See `LICENSE`.
