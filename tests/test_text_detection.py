from updatemenow.text_detection import categorize, extract_cves, match_terms


def test_extract_cves_normalizes_case_and_dedupes() -> None:
    cves = extract_cves("Issue CVE-2026-12345", "duplicate cve-2026-12345")

    assert cves == ["CVE-2026-12345"]


def test_match_terms_is_case_insensitive_and_preserves_config_terms() -> None:
    matches = match_terms("Fortinet ransomware advisory", ["fortinet", "Ransomware", "missing"])

    assert matches == ["fortinet", "Ransomware"]


def test_categorize_uses_first_matching_rule() -> None:
    category = categorize("CVE-2026-12345 actively exploited", "Patch available")

    assert category == "Exploited Vulnerability"
