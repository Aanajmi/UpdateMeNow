from datetime import datetime, timedelta, timezone

from updatemenow.dedupe import canonicalize_url, dedupe_items, normalize_title
from updatemenow.filters import filter_by_keywords, filter_by_time
from updatemenow.models import CyberUpdateItem, DedupeMode, ScanRequest, SourceType


NOW = datetime(2026, 5, 20, 18, 0, tzinfo=timezone.utc)


def test_filter_by_time_excludes_old_and_unknown_dates() -> None:
    items = [
        _item("recent", NOW - timedelta(hours=2)),
        _item("old", NOW - timedelta(hours=7)),
        _item("unknown", None),
    ]

    filtered = filter_by_time(items, ScanRequest(hours=6), now=NOW)

    assert [item.id for item in filtered] == ["recent"]


def test_filter_by_keywords_uses_inclusive_request_keywords() -> None:
    items = [
        _item("ransomware", NOW, keywords_matched=["ransomware"]),
        _item("fortinet", NOW, keywords_matched=["Fortinet"]),
        _item("none", NOW, keywords_matched=[]),
    ]

    filtered = filter_by_keywords(items, ScanRequest(keywords=["fortinet", "zero-day"]))

    assert [item.id for item in filtered] == ["fortinet"]


def test_dedupe_strict_removes_duplicate_urls_and_same_source_titles() -> None:
    items = [
        _item("first", NOW, url="https://example.com/a?id=1&utm_source=news", title="Same Title"),
        _item("dupe-url", NOW, url="https://EXAMPLE.com/a/?id=1#section", title="Different Title"),
        _item("dupe-title", NOW, url="https://example.com/b", title=" same   title "),
        _item("different-source", NOW, source_id="other", title="Same Title"),
    ]

    deduped, duplicates_removed = dedupe_items(items, DedupeMode.STRICT)

    assert [item.id for item in deduped] == ["first", "different-source"]
    assert duplicates_removed == 2


def test_dedupe_normal_removes_same_group_titles_across_sources() -> None:
    items = [
        _item("first", NOW, source_id="source-a", source_group="government", title="Same Title"),
        _item("same-group", NOW, source_id="source-b", source_group="government", title=" same title "),
        _item("different-group", NOW, source_id="source-c", source_group="security_news", title="Same Title"),
    ]

    deduped, duplicates_removed = dedupe_items(items, DedupeMode.NORMAL)

    assert [item.id for item in deduped] == ["first", "different-group"]
    assert duplicates_removed == 1


def test_dedupe_relaxed_removes_near_duplicate_cross_source_items() -> None:
    items = [
        _item(
            "first",
            NOW,
            source_id="vuln-db",
            source_group="vulnerability_database",
            title="Fortinet fixes CVE-2026-12345 in FortiOS",
            cves=["CVE-2026-12345"],
            vendors_matched=["Fortinet"],
        ),
        _item(
            "second",
            NOW + timedelta(minutes=10),
            source_id="news",
            source_group="security_news",
            title="Fortinet fixes CVE-2026-12345 in FortiOS",
            cves=["CVE-2026-12345"],
            vendors_matched=["Fortinet"],
        ),
    ]

    deduped, duplicates_removed = dedupe_items(items, DedupeMode.RELAXED)

    assert [item.id for item in deduped] == ["first"]
    assert duplicates_removed == 1


def test_normalize_title_collapses_whitespace() -> None:
    assert normalize_title(" A   Test\nTitle ") == "a test title"


def test_canonicalize_url_removes_tracking_and_sorts_query() -> None:
    url = "HTTPS://Example.com/path/?utm_source=email&b=2&a=1&fbclid=abc#section"

    assert canonicalize_url(url) == "https://example.com/path?a=1&b=2"


def _item(
    item_id: str,
    published_at: datetime | None,
    source_id: str = "source",
    source_group: str = "government",
    title: str | None = None,
    url: str = "",
    cves: list[str] | None = None,
    keywords_matched: list[str] | None = None,
    vendors_matched: list[str] | None = None,
) -> CyberUpdateItem:
    return CyberUpdateItem(
        id=item_id,
        source_id=source_id,
        source_name="Source",
        source_group=source_group,
        source_type=SourceType.API,
        published_at=published_at,
        title=title or item_id,
        description="Description",
        url=url,
        cves=cves or [],
        keywords_matched=keywords_matched or [],
        vendors_matched=vendors_matched or [],
        scan_run_time=NOW,
    )
