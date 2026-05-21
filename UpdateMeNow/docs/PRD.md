Product Requirements Document
UpdateMeNow v1 — CLI Cybersecurity Update Reporter

Project name: UpdateMeNow
CLI command: umn
License: MIT
Version target: v1.0
Primary format: Command-line tool
Primary export: Excel
Default command:

umn scan

By default, umn scan should scan the last 6 hours, use all enabled default sources, and export results to Excel.

This PRD is based on your original UpdateMeNow vision and the simplified v1 decisions we refined.

1. Product summary

UpdateMeNow is a cross-platform cybersecurity update tracking tool that helps technical users quickly collect recent cybersecurity advisories, CVEs, vulnerability updates, and security news from free public sources.

The v1 product is intentionally simple:

Run one command, collect recent cybersecurity updates, group them by source, sort newest to oldest, and export a clean Excel report.

UpdateMeNow v1 is not a threat intelligence platform yet. It is a reliable, beginner-friendly CLI tool for generating fast cybersecurity update reports.

2. Target users
Primary user

The primary v1 user is:

A technical individual who wants a personal cybersecurity news/advisory tracker and is comfortable cloning a GitHub repo, editing config files, and running CLI commands.

This includes:

You
Cybersecurity students
IT admins
SOC learners
Home lab users
Technical hobbyists
Small team analysts who want a lightweight report generator
User skill level

The tool should be:

Easy enough for beginners to run
Clear enough for students to understand
Useful enough for technical users to customize
Simple enough for contributors to extend

The language should be a mix of beginner-friendly and analyst-friendly.

3. Product goals
v1 goals
Provide a simple command-line cybersecurity update scanner.
Work on macOS, Windows, and Linux.
Use only free public RSS feeds and official public APIs.
Avoid scraping entirely.
Export a clean Excel report by default.
Allow users to scan recent time windows such as 6 hours, 24 hours, 72 hours, or 7 days.
Allow users to filter by source, keyword, CVE, vendor, and category.
Group report results by source.
Sort results newest to oldest within each source.
Make the GitHub repository polished, understandable, and easy to contribute to.
v1 non-goals

The following are not included in v1:

Web dashboard
User accounts
Team workspaces
Scheduling
SQLite database
PostgreSQL database
AI-generated summaries
Priority scoring
“Why it matters” fields
Suggested analyst actions
PDF export
Email, Slack, or Discord alerts
Web scraping
Paid APIs
Sample reports or sample datasets
4. Core user experience
Default experience

The simplest command should be:

umn scan

Expected behavior:

Scan the last 6 hours
Use all enabled default sources
Export to Excel
Save the report in the local reports/ folder
Print a terminal summary

Example terminal output:

UpdateMeNow Cyber Update Scan

Scan range: Last 6 hours
Sources scanned: 12
Raw items collected: 74
Duplicates removed: 9
Final items: 65

Report exported:
reports/UpdateMeNow_Report_2026-05-20_6h.xlsx
Main “wow moment”

A user installs the tool, runs:

umn scan

Then quickly receives a clean Excel report showing recent cybersecurity updates grouped by trusted source and sorted newest first.

5. Functional requirements
5.1 CLI command

The CLI command must be:

umn

The main scan command must be:

umn scan
5.2 Default scan behavior

When the user runs:

umn scan

The tool must use these defaults:

Setting	Default
Time range	Last 6 hours
Sources	All enabled default sources
Export format	Excel
Output folder	reports/
Sorting	Source order, then newest to oldest
Scraping	Disabled / not implemented
Paid APIs	Not supported
5.3 Scan time range

The user must be able to scan by hours:

umn scan --hours 24

The user must be able to scan by days:

umn scan --days 7

Rules:

--hours and --days should not be used together.
If neither is provided, use --hours 6.
5.4 Source filtering

The user must be able to scan a specific source:

umn scan --source nvd

The user must be able to scan multiple sources:

umn scan --source cisa --source nvd --source github

Optional shorthand for later:

umn scan --sources cisa,nvd,github

For v1, repeated --source flags are cleaner and easier to implement reliably.

5.5 Keyword filtering

The user must be able to filter by keyword:

umn scan --keyword ransomware

The user must be able to provide multiple keywords:

umn scan --keyword ransomware --keyword fortinet --keyword zero-day

Keyword matching should be inclusive:

ransomware OR fortinet OR zero-day
5.6 CVE detection

The tool must detect CVE identifiers in titles and descriptions.

Example:

CVE-2026-12345

Detected CVEs should appear in the Excel report.

5.7 Vendor/product matching

The tool must detect vendors and products from a configurable watchlist.

Example vendors:

Microsoft
Cisco
Fortinet
Palo Alto
Ivanti
VMware
Atlassian
Okta
GitHub
Google
AWS
Azure

The user can edit the config file directly.

No weighted vendor matching is required for v1.

5.8 Duplicate handling

The tool should remove obvious duplicates.

Initial v1 duplicate logic:

Same URL = duplicate
Same normalized title + same source = duplicate

Near-duplicate detection can wait until a later version.

5.9 Sorting and grouping

The report must be grouped by source importance order.

Within each source group, items must be sorted newest to oldest.

Recommended default source order:

1. CISA KEV
2. CISA Advisories
3. NVD CVEs
4. GitHub Security Advisories
5. Vendor advisories
6. CERT/CC
7. SANS ISC
8. BleepingComputer
9. KrebsOnSecurity
10. Other security news

No priority scoring is required in v1.

6. Export requirements
6.1 Default export

Default export format:

Excel

So this:

umn scan

Is equivalent to:

umn scan --hours 6 --export excel
6.2 Supported v1 exports

v1 should support:

umn scan --export excel
umn scan --export json
umn scan --export excel,json
6.3 Excel report

The Excel report should use one worksheet.

Worksheet name:

Cyber Updates

Required columns:

Column	Description
Source Group	Government, CVE Database, Vendor Advisory, Security News, etc.
Source Name	Human-readable source name
Source Type	RSS or API
Published Date	Original published timestamp
Age	Example: 2h ago, 1d ago
Title	Article/advisory title
Description	RSS/API description or summary
URL	Clickable source URL
CVEs	CVEs detected in title/description
Keywords Matched	User/default keywords matched
Vendors/Products Matched	Watchlist vendors/products detected
Category	Basic category
Scan Run Time	Timestamp when scan was run
6.4 Excel formatting

The Excel export must include:

One sheet only
Bold headers
Freeze top row
Auto-filter enabled
Auto-fit column widths
Clickable URLs
Source-grouped rows
Newest-first ordering inside each source group
Timestamped filename

Example filename:

UpdateMeNow_Report_2026-05-20_6h.xlsx

For custom time ranges:

UpdateMeNow_Report_2026-05-20_24h.xlsx
UpdateMeNow_Report_2026-05-20_7d.xlsx
6.5 JSON export

The JSON export should include:

Scan metadata
Source metadata
Final collected items
Detected CVEs
Matched keywords
Matched vendors/products

Example structure:

{
  "scan": {
    "run_time": "2026-05-20T14:30:00Z",
    "range": "6h",
    "sources_scanned": 12,
    "raw_items": 74,
    "duplicates_removed": 9,
    "final_items": 65
  },
  "items": []
}
7. Source requirements
7.1 Source policy

v1 sources must be:

Free
Public
RSS-based or official API-based
Configurable
Respectful of rate limits
Non-scraping
7.2 Excluded source types

v1 must not use:

Paid APIs
Login-only sources
Aggressive scraping
Browser automation
CAPTCHA bypassing
Private feeds
Anything that violates source terms
7.3 Configurable sources

Sources should be defined in:

config/sources.yaml

Example format:

sources:
  - id: cisa_alerts
    name: CISA Alerts
    group: government
    type: rss
    url: "SOURCE_URL_HERE"
    enabled: true
    default_order: 20

  - id: nvd
    name: NVD CVEs
    group: vulnerability_database
    type: api
    provider: nvd
    enabled: true
    default_order: 30
7.4 Source testing

v1 should include:

umn sources list
umn sources test

umn sources list should show configured sources.

umn sources test should check whether enabled sources are reachable.

8. Configuration requirements
8.1 Config initialization

The user should be able to create default config files:

umn config init

This should create:

config/sources.yaml
config/keywords.yaml
8.2 Config validation

The user should be able to validate config files:

umn config validate

Validation should check:

Required fields exist
Source IDs are unique
Enabled sources have URLs or providers
Source types are supported
Keyword files are valid YAML
Vendor watchlists are valid lists
8.3 Keywords config

Example:

watchlists:
  default:
    - ransomware
    - zero-day
    - exploited
    - phishing
    - supply chain
    - malware
    - data breach
    - vulnerability
    - CVE

  vendors:
    - Microsoft
    - Fortinet
    - Cisco
    - Palo Alto
    - Ivanti
    - VMware
    - Atlassian
    - Okta
    - GitHub
    - Google
    - AWS
    - Azure

v1 does not need command-level watchlist switching.

Users can edit the file manually.

9. CLI command specification
Required v1 commands
umn scan
umn scan --hours 24
umn scan --days 7
umn scan --source nvd
umn scan --source cisa_kev
umn scan --keyword ransomware
umn scan --export excel
umn scan --export json
umn scan --export excel,json
umn sources list
umn sources test
umn config init
umn config validate
Default scan command
umn scan

Equivalent behavior:

umn scan --hours 6 --export excel
Commands excluded from v1

These should wait:

umn schedule setup
umn report open latest
umn report summarize latest
umn dashboard
umn serve
umn stats
10. Technical requirements
Recommended language

Python.

Recommended libraries
Purpose	Library
CLI	Typer
Terminal output	Rich
RSS parsing	feedparser
HTTP requests	httpx
Config validation	Pydantic
YAML parsing	PyYAML or ruamel.yaml
Excel export	openpyxl
Testing	pytest
Cross-platform requirement

The tool should run on:

macOS
Windows
Linux

Avoid OS-specific behavior in v1.

Python version

Recommended:

Python 3.11+
11. Data model
CyberUpdateItem

Core fields:

id
source_id
source_name
source_group
source_type
published_at
title
description
url
cves
keywords_matched
vendors_matched
category
raw_data
scan_run_time
ScanResult

Core fields:

scan_id
started_at
ended_at
range_hours
sources_requested
sources_scanned
raw_item_count
duplicates_removed
final_item_count
items
export_paths
12. Categories

v1 should use simple rule-based categories.

Suggested categories:

Vulnerability
Exploited Vulnerability
Ransomware
Phishing
Data Breach
Malware
Cloud Security
Identity / Access
Supply Chain
Patch / Update
Threat Actor
Vendor Advisory
Government Advisory
Security News
General

Category detection should be basic and transparent.

No ML classification is needed.

13. Safety and ethics requirements

UpdateMeNow v1 must include a safety statement in the README and documentation.

Required safety principles:

Defensive and educational use only
No exploitation support
No phishing support
No malware support
No credential theft support
No offensive automation
No scraping in v1
Respect source terms
Respect rate limits
Use RSS feeds and official APIs where available
Do not overload websites

The tool should be positioned as a reporting and awareness tool, not an exploitation tool.

14. GitHub repository requirements

The repository should include:

README.md
LICENSE
SECURITY.md
CONTRIBUTING.md
pyproject.toml
.gitignore
config/sources.yaml
config/keywords.yaml
src/updatemenow/
tests/

Do not include sample reports or sample datasets in v1.

README should include:

What UpdateMeNow is
What it does not do
Installation
Quick start
Default command
Example commands
Config explanation
Excel export explanation
Source safety policy
Roadmap
Contribution notes
MIT license notice
15. Acceptance criteria

v1 is complete when:

User can install the project locally.
User can run:
umn scan
The command scans the last 6 hours.
The command uses all enabled default sources.
The command exports an Excel report.
The Excel file is saved in reports/.
The Excel file has one clean worksheet.
Rows are grouped by source.
Rows are sorted newest to oldest inside each source group.
CVEs are detected.
Keywords are matched.
Vendors/products are matched.
Duplicate URLs are removed.
JSON export works.
umn sources list works.
umn sources test works.
umn config init works.
umn config validate works.
No scraping exists in the codebase.
No paid APIs are required.
README clearly explains how to use the tool.
16. Recommended v1 milestone plan
Milestone 1 — Project foundation
Create Python package
Add Typer CLI
Add config loading
Add basic models
Add README draft
Add MIT license
Milestone 2 — RSS collection
Add RSS collector
Add source config support
Add source listing
Add source testing
Milestone 3 — API collectors
Add NVD collector
Add CISA KEV collector
Add GitHub advisories collector if practical without requiring paid access
Milestone 4 — Processing pipeline
Normalize collected items
Filter by time range
Filter by source
Filter by keyword
Extract CVEs
Match vendors/products
Remove duplicates
Sort/group results
Milestone 5 — Exports
Add Excel export
Add JSON export
Add timestamped filenames
Add terminal summary
Milestone 6 — Polish
Add tests
Improve error messages
Add config validation
Add source testing
Improve README
Add contribution docs
Prepare v1 release tag
17. Final v1 definition

UpdateMeNow v1 is successful when a user can run:

umn scan

And receive a clean Excel report of cybersecurity updates from the last 6 hours, grouped by trusted source, sorted newest to oldest, using only free public RSS feeds and official APIs.
