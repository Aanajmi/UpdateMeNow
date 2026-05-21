# UpdateMeNow

UpdateMeNow is a Python command-line tool that collects recent cybersecurity updates from RSS feeds and official APIs, then turns them into a clean Excel report.

It is built for people who want a quick snapshot of recent advisories, CVEs, vendor updates, and security news without manually checking a long list of websites.

Run one command:

```bash
umn
```

Get a report:

```text
reports/UpdateMeNow_Report_YYYY-MM-DD_6h.xlsx
```

## What It Does

UpdateMeNow helps you:

- collect recent cybersecurity updates from configured sources
- scan the last 6 hours by default
- export results to Excel by default
- optionally export results to JSON
- filter by source, keyword, vendor, or time range
- detect CVEs in titles and descriptions
- match vendors and products from a configurable watchlist
- remove obvious duplicates
- group results by source
- sort results newest to oldest

## What It Does Not Do

UpdateMeNow v1 intentionally stays focused and safe:

- no web scraping
- no browser automation
- no paid APIs
- no database
- no dashboard
- no scheduling
- no alerting
- no AI-generated summaries
- no exploitation, phishing, malware, or offensive automation support

This is a reporting and awareness tool, not an offensive security tool.

## Quick Start

### Option 1: Clone the Repo and Install Locally

Use this option if you want to run the project, modify it, or contribute.

```bash
git clone https://github.com/Aanajmi/UpdateMeNow.git
cd UpdateMeNow
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
umn --help
umn
```

After installation, the `umn` command works because the package defines a console script entry point in `pyproject.toml`.

To confirm your shell is using the local installed command:

```bash
which umn
```

You should see a path inside your virtual environment, similar to:

```text
/path/to/UpdateMeNow/.venv/bin/umn
```

### Option 2: Install Directly from GitHub with pipx

Use this option if you want `umn` available as a normal command without manually activating a virtual environment.

On macOS:

```bash
brew install pipx
pipx ensurepath
pipx install git+https://github.com/Aanajmi/UpdateMeNow.git
umn --help
umn
```

If `umn` is not found after `pipx ensurepath`, close and reopen your terminal, then try again.

## Requirements

- Python 3.11 or newer
- Git
- Internet access for RSS feeds and official APIs

Check your Python version:

```bash
python3 --version
```

If your system has multiple Python versions, use a specific one when creating the virtual environment:

```bash
python3.11 -m venv .venv
```

or:

```bash
python3.12 -m venv .venv
```

## Install and Run by Operating System

### macOS

```bash
git clone https://github.com/Aanajmi/UpdateMeNow.git
cd UpdateMeNow
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
umn
```

### Linux

```bash
git clone https://github.com/Aanajmi/UpdateMeNow.git
cd UpdateMeNow
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
umn
```

### Windows PowerShell

```powershell
git clone https://github.com/Aanajmi/UpdateMeNow.git
cd UpdateMeNow
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
umn
```

If PowerShell blocks activation scripts, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the virtual environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## CLI Overview

```text
umn
├── scan
├── config init
├── config validate
├── sources list
└── sources test
```

Running `umn` with no arguments runs the default scan.

```bash
umn
```

That is equivalent to:

```bash
umn scan --hours 6 --export excel
```

## Commands

### Scan for Updates

```bash
umn scan
```

Common examples:

```bash
umn scan --hours 24
umn scan --days 7
umn scan --source nvd
umn scan --source cisa_kev --source github
umn scan --keyword ransomware
umn scan --keyword ransomware --keyword fortinet
umn scan --export excel
umn scan --export json
umn scan --export excel,json
```

### Initialize Config Files

```bash
umn config init
```

Overwrite existing local config files:

```bash
umn config init --force
```

### Validate Config Files

```bash
umn config validate
```

### List Sources

```bash
umn sources list
```

### Test Sources

```bash
umn sources test
umn sources test --all
umn sources test --timeout 20
```

## Configuration

Editable configuration files live in:

```text
config/sources.yaml
config/keywords.yaml
```

Use `sources.yaml` to control where updates come from.

Use `keywords.yaml` to control keyword and vendor matching.

Example workflow:

```bash
umn config init
umn config validate
umn sources list
umn sources test
umn scan
```

## Report Output

By default, reports are saved in:

```text
reports/
```

Example filename:

```text
reports/UpdateMeNow_Report_2026-05-20_6h.xlsx
```

The Excel report includes:

- one worksheet named `Cyber Updates`
- bold headers
- frozen top row
- filters
- clickable URLs
- source name and source group
- published date and age
- title and description
- detected CVEs
- matched keywords
- matched vendors/products
- basic category
- scan run time

JSON export is also available:

```bash
umn scan --export json
```

## Duplicate Handling

Duplicate handling can be adjusted with `--dedupe`:

```bash
umn scan --dedupe strict
umn scan --dedupe normal
umn scan --dedupe relaxed
```

Modes:

- `strict`: removes same-URL duplicates and same-source title duplicates
- `normal`: also removes same-title items within the same source group
- `relaxed`: collapses likely duplicates when title, CVE, vendor, and timing signals line up

## Development

Install with development dependencies:

```bash
git clone https://github.com/Aanajmi/UpdateMeNow.git
cd UpdateMeNow
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest
```

Run config checks:

```bash
umn config validate
umn sources test
```

Useful project files:

```text
README.md
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
docs/
config/
src/updatemenow/
tests/
```

## Safety and Responsible Use

UpdateMeNow is intended for defensive security awareness, learning, and reporting.

The project uses configured RSS feeds and official APIs. It does not include web scraping, offensive automation, phishing support, malware support, credential theft support, or exploitation features.

Use sources respectfully and avoid overloading websites or ignoring source terms.

## Roadmap

Planned v1 milestones:

- project foundation
- config commands
- source commands
- RSS/API collectors
- processing pipeline
- Excel and JSON exports
- release polish

Possible future improvements:

- more official API collectors
- improved vendor matching
- better source testing
- Markdown export
- scheduled local reports
- optional dashboard

## Contributing

Contributions are welcome.

Good first contribution ideas:

- add a new RSS source
- improve documentation
- add tests
- improve error messages
- improve source validation
- refine category detection

Before opening a pull request, run:

```bash
python -m pytest
umn config validate
```

## License

MIT. See `LICENSE`.
