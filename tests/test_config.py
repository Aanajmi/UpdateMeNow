from pathlib import Path

from updatemenow.config import load_default_keywords, load_default_sources, load_sources


EXPECTED_ENABLED_SOURCE_IDS = [
    "cisa_kev",
    "cisa_alerts",
    "uscert_current_activity",
    "uk_ncsc_alerts",
    "cert_eu_advisories",
    "canada_cyber_centre",
    "nvd",
    "github",
    "certcc_vuls",
    "sans_isc",
    "bleepingcomputer",
    "krebsonsecurity",
]


def test_load_default_sources() -> None:
    sources = load_default_sources()

    assert [source.id for source in sources.enabled_sources] == EXPECTED_ENABLED_SOURCE_IDS


def test_default_sources_include_expanded_optional_catalog() -> None:
    sources = load_default_sources()
    sources_by_id = {source.id: source for source in sources.sources}

    assert len(sources.sources) == 35
    assert sources_by_id["mandiant_threat_research"].url == (
        "https://feeds.feedburner.com/threatintelligence/pvexyqv7v0v"
    )
    assert sources_by_id["google_project_zero"].url == "https://projectzero.google/feed.xml"
    assert not sources_by_id["exploit_db"].enabled
    assert not sources_by_id["the_hacker_news"].enabled


def test_local_sources_match_packaged_defaults() -> None:
    local_sources = load_sources(Path("config/sources.yaml"))
    default_sources = load_default_sources()

    assert local_sources == default_sources


def test_load_default_keywords() -> None:
    keywords = load_default_keywords()

    assert "ransomware" in keywords.default_keywords
    assert "Microsoft" in keywords.vendors
