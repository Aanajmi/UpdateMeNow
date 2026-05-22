from __future__ import annotations

import re

CVE_PATTERN = re.compile(r"\bCVE-\d{4}-\d{4,10}\b", re.IGNORECASE)

CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Exploited Vulnerability", ("known exploited", "exploited in the wild", "actively exploited")),
    ("Ransomware", ("ransomware",)),
    ("Phishing", ("phishing",)),
    ("Data Breach", ("data breach", "breach", "leaked data")),
    ("Malware", ("malware", "trojan", "backdoor")),
    ("Cloud Security", ("aws", "azure", "gcp", "cloud")),
    ("Identity / Access", ("identity", "authentication", "authorization", "credential")),
    ("Supply Chain", ("supply chain", "dependency confusion", "package registry")),
    ("Patch / Update", ("patch", "update", "security update", "fixed in")),
    ("Threat Actor", ("threat actor", "apt", "nation-state")),
    ("Vendor Advisory", ("advisory", "security advisory")),
    ("Government Advisory", ("cisa", "cert/cc", "government")),
    ("Vulnerability", ("cve-", "vulnerability", "cvss")),
    ("Security News", ("security news", "incident", "attack")),
)


def extract_cves(*values: str) -> list[str]:
    matches: set[str] = set()
    for value in values:
        matches.update(match.upper() for match in CVE_PATTERN.findall(value or ""))
    return sorted(matches)


def match_terms(text: str, terms: list[str]) -> list[str]:
    normalized_text = text.casefold()
    matched: list[str] = []
    seen: set[str] = set()

    for term in terms:
        normalized_term = term.strip()
        if not normalized_term:
            continue
        key = normalized_term.casefold()
        if key in seen:
            continue
        if key in normalized_text:
            matched.append(normalized_term)
            seen.add(key)

    return matched


def categorize(title: str, description: str, fallback: str = "General") -> str:
    text = f"{title} {description}".casefold()
    for category, terms in CATEGORY_RULES:
        if any(term in text for term in terms):
            return category
    return fallback or "General"
