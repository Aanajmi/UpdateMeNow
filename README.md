# UpdateMeNow

UpdateMeNow is a Python 3.11+ command-line tool that collects recent cybersecurity updates from free public RSS feeds and official public APIs, then exports a clean Excel report.

The default command is simple:

```bash
umn
```

That scans the last 6 hours, removes obvious duplicates, detects CVEs and keyword/vendor matches, and writes a report into `reports/`.

## Table Of Contents

- [What It Does](#what-it-does)
- [Install From GitHub](#install-from-github)
- [Run UpdateMeNow](#run-updatemenow)
- [Common Commands](#common-commands)
- [Configuration](#configuration)
- [Report Output](#report-output)
- [Troubleshooting](#troubleshooting)
- [Development And Testing](#development-and-testing)
- [Safety](#safety)
- [License](#license)

## What It Does

UpdateMeNow helps you keep a local cybersecurity update report without manually checking many sites.

It collects from:

- government advisories
- vulnerability trackers
- vendor security blogs
- threat research feeds
- security news outlets

It can:

- scan recent cybersecurity updates
- default to the last 6 hours
- export Excel by default
- export JSON when requested
- detect CVEs, keywords, vendors/products, and broad categories
- filter by source or keyword
- remove obvious duplicates
- list and test configured sources

It does not include scraping, browser automation, paid APIs, a database, a dashboard, scheduling, alerting, AI summaries, or offensive security automation.

## Install From GitHub

Use these steps if you just want to download the repository from GitHub and run `umn` from anywhere.

Project page: [https://github.com/Aanajmi/UpdateMeNow/tree/main](https://github.com/Aanajmi/UpdateMeNow/tree/main)

### 1. Install Python

Install Python 3.11 or newer.

Check your version:

#### Mac Or Linux

```bash
python3 --version
```

#### Windows

Open PowerShell and run:

```powershell
python --version
```

### 2. Download The Repository

Use either the browser download or Git.

#### Option A: Download ZIP

1. Open [https://github.com/Aanajmi/UpdateMeNow/tree/main](https://github.com/Aanajmi/UpdateMeNow/tree/main).
2. Click the green `Code` button.
3. Click `Download ZIP`.
4. Unzip the file.
5. The folder will usually be named `UpdateMeNow-main`.

#### Option B: Use Git

```bash
git clone https://github.com/Aanajmi/UpdateMeNow.git
cd UpdateMeNow
```

### 3. Open A Terminal In The Project Folder

If you downloaded the ZIP, go into the unzipped folder.

#### Mac Or Linux Example

```bash
cd ~/Downloads/UpdateMeNow-main
```

#### Windows Example

```powershell
cd C:\Users\YourName\Downloads\UpdateMeNow-main
```

If your folder is somewhere else, use that folder path instead.

### 4. Install `pipx`

`pipx` installs command-line Python apps so the `umn` command works from any folder.

#### Mac Or Linux

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Close and reopen your terminal after `ensurepath`.

#### Windows

In PowerShell:

```powershell
python -m pip install --user pipx
python -m pipx ensurepath
```

Close and reopen PowerShell after `ensurepath`.

### 5. Install UpdateMeNow

Run this from inside the project folder:

```bash
pipx install .
```

If you already installed UpdateMeNow and want to refresh it from the latest local copy, run:

```bash
pipx install --force .
```

## Run UpdateMeNow

Check that the command is installed:

```bash
umn --version
```

Run the default scan:

```bash
umn
```

This is the same as:

```bash
umn scan --hours 6 --export excel
```

You do not need to create config files before running `umn`. If local files do not exist at `config/sources.yaml` and `config/keywords.yaml`, UpdateMeNow uses the packaged default config included with the app.

Only create local config files if you want to edit sources or keywords:

```bash
umn config init
```

## Common Commands

### Scan

```bash
umn
umn scan
umn scan --hours 24
umn scan --days 7
umn scan --export excel,json
```

### Filter A Scan

```bash
umn scan --source nvd
umn scan --source cisa_kev --source github
umn scan --keyword ransomware
umn scan --keyword fortinet --keyword zero-day
```

### Change Duplicate Handling

```bash
umn scan --dedupe strict
umn scan --dedupe normal
umn scan --dedupe relaxed
```

- `strict` keeps only same-URL and same-source title duplicates.
- `normal` also removes same-title items within the same source group.
- `relaxed` can collapse obvious cross-feed near-duplicates when the title, CVE, vendor, and timing signals line up.

### Manage Config

```bash
umn config init
umn config init --force
umn config validate
```

### Inspect Sources

```bash
umn sources list
umn sources test
umn sources test --all
umn sources test --timeout 20
```

## Configuration

UpdateMeNow has two kinds of config:

- Packaged defaults in `src/updatemenow/defaults/`
- Editable local files in `config/`

Runtime commands such as `umn`, `umn scan`, and `umn sources list` use packaged defaults when local config files do not exist.

If you want editable local files, run:

```bash
umn config init
```

That creates:

- `config/sources.yaml`
- `config/keywords.yaml`

Then validate them:

```bash
umn config validate
```

`umn config validate` is intentionally strict. It validates local editable config files, so it will report missing files until you run `umn config init`.

## Report Output

By default, scans write an Excel workbook into `reports/`:

```text
reports/UpdateMeNow_Report_2026-05-20_6h.xlsx
```

The workbook includes:

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

## Troubleshooting

### `umn` Is Not Found

Close and reopen your terminal after running:

```bash
python3 -m pipx ensurepath
```

On Windows, use:

```powershell
python -m pipx ensurepath
```

Then check:

```bash
pipx --version
umn --version
```

### `pipx` Is Not Found

Install it again:

#### Mac Or Linux

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

#### Windows

```powershell
python -m pip install --user pipx
python -m pipx ensurepath
```

Close and reopen your terminal.

### `Config is invalid` And Says Config Files Are Missing

Bare `umn`, `umn scan`, and `umn sources list` should not fail just because you are running from a folder without `config/`. They fall back to packaged defaults.

`umn config validate` is different. It checks local editable config files. If you want local files to validate or customize, run:

```bash
umn config init
umn config validate
```

If you installed an older local copy with `pipx`, reinstall from the updated project folder:

```bash
pipx install --force .
```

### Windows Says `python` Is Not Found

Install Python from `https://www.python.org/downloads/`.

During installation, enable the option that adds Python to `PATH`, then close and reopen PowerShell.

## Development And Testing

For local development:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Release-readiness guidance lives in:

- `docs/RELEASE_CHECKLIST.md`
- `CHANGELOG.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/PUBLIC_RELEASE.md`

## Safety

UpdateMeNow is for defensive and educational reporting only. It does not provide offensive capability, scraping, phishing support, malware support, credential theft support, browser automation, or CAPTCHA bypassing.

Use configured public sources respectfully, and avoid overloading websites or ignoring source terms.

## License

MIT. See `LICENSE`.
