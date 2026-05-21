from datetime import datetime, timedelta, timezone

import pytest

from updatemenow.models import CyberUpdateItem, KeywordConfig, ScanRequest, SourceCatalog, SourceConfig, SourceType
from updatemenow.pipeline import PipelineError, enrich_items, run_scan, select_sources, sort_items


NOW = datetime.now(timezone.utc)


def test_select_sources_rejects_unknown_or_disabled_source() -> None:
    catalog = SourceCatalog(
        sources=[
            _source("enabled", enabled=True),
            _source("disabled", enabled=False),
        ]
    )

    with pytest.raises(PipelineError) as exc_info:
        select_sources(catalog, ["disabled", "missing"])

    assert "Unknown or disabled source ID: disabled, missing" in str(exc_info.value)
    assert "Enabled source IDs: enabled" in str(exc_info.value)


def test_select_sources_dedupes_repeated_requested_sources() -> None:
    catalog = SourceCatalog(sources=[_source("nvd")])

    selected = select_sources(catalog, ["nvd", "nvd"])

    assert [source.id for source in selected] == ["nvd"]


def test_enrich_items_detects_cves_keywords_vendors_and_category() -> None:
    item = _item(
        "item-1",
        title="Fortinet advisory for CVE-2026-12345",
        description="Actively exploited ransomware vulnerability.",
    )

    enriched = enrich_items(
        [item],
        default_keywords=["ransomware", "exploited"],
        request_keywords=["fortinet"],
        vendors=["Fortinet"],
    )

    assert enriched[0].cves == ["CVE-2026-12345"]
    assert enriched[0].keywords_matched == ["ransomware", "exploited", "fortinet"]
    assert enriched[0].vendors_matched == ["Fortinet"]
    assert enriched[0].category == "Exploited Vulnerability"


def test_sort_items_groups_by_source_order_then_newest_first() -> None:
    sources = [_source("cisa"), _source("nvd")]
    items = [
        _item("nvd-old", source_id="nvd", published_at=NOW - timedelta(hours=2)),
        _item("cisa-old", source_id="cisa", published_at=NOW - timedelta(hours=4)),
        _item("cisa-new", source_id="cisa", published_at=NOW - timedelta(hours=1)),
    ]

    sorted_items = sort_items(items, sources)

    assert [item.id for item in sorted_items] == ["cisa-new", "cisa-old", "nvd-old"]


def test_run_scan_processes_collected_items_and_exports_report(monkeypatch, tmp_path) -> None:
    catalog = SourceCatalog(sources=[_source("cisa"), _source("nvd")])
    keyword_config = KeywordConfig(
        watchlists={
            "default": ["ransomware"],
            "vendors": ["Fortinet"],
        }
    )

    def fake_collect_sources(selected_catalog, request, client=None):
        assert [source.id for source in selected_catalog.sources] == ["nvd"]
        return [
            _item(
                "raw-1",
                source_id="nvd",
                title="Fortinet CVE-2026-12345 ransomware advisory",
                url="https://example.com/a",
                published_at=NOW - timedelta(hours=1),
            ),
            _item(
                "raw-2",
                source_id="nvd",
                title="Duplicate ransomware",
                url="https://example.com/a",
                published_at=NOW - timedelta(hours=1),
            ),
            _item(
                "old",
                source_id="nvd",
                title="Old ransomware",
                url="https://example.com/old",
                published_at=NOW - timedelta(hours=10),
            ),
        ]

    monkeypatch.setattr("updatemenow.pipeline.collect_sources", fake_collect_sources)

    result = run_scan(
        request=ScanRequest(hours=6, sources_requested=["nvd"], keywords=["ransomware"]),
        sources=catalog,
        keywords=keyword_config,
        output_dir=tmp_path,
    )

    assert result.sources_scanned == 1
    assert result.raw_item_count == 3
    assert result.duplicates_removed == 1
    assert result.final_item_count == 1
    assert result.items[0].cves == ["CVE-2026-12345"]
    assert result.items[0].vendors_matched == ["Fortinet"]
    assert len(result.export_paths) == 1
    assert result.export_paths[0].endswith(".xlsx")


def _source(source_id: str, enabled: bool = True) -> SourceConfig:
    return SourceConfig(
        id=source_id,
        name=source_id.upper(),
        group="government",
        type=SourceType.API,
        provider="cisa_kev",
        enabled=enabled,
        default_order=10 if source_id == "cisa" else 20,
    )


def _item(
    item_id: str,
    source_id: str = "cisa",
    title: str = "Title",
    description: str = "Description",
    url: str = "",
    published_at: datetime | None = None,
) -> CyberUpdateItem:
    return CyberUpdateItem(
        id=item_id,
        source_id=source_id,
        source_name=source_id.upper(),
        source_group="government",
        source_type=SourceType.API,
        published_at=published_at or NOW,
        title=title,
        description=description,
        url=url,
        scan_run_time=NOW,
    )
