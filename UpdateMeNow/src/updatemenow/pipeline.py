from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx

from updatemenow.dedupe import dedupe_items
from updatemenow.exporters import export_reports
from updatemenow.exporters.common import REPORTS_DIR
from updatemenow.filters import filter_by_keywords, filter_by_time
from updatemenow.models import CyberUpdateItem, KeywordConfig, ScanRequest, ScanResult, SourceCatalog, SourceConfig
from updatemenow.sources.collectors import collect_sources
from updatemenow.text_detection import categorize, extract_cves, match_terms


class PipelineError(RuntimeError):
    pass


def run_scan(
    request: ScanRequest,
    sources: SourceCatalog,
    keywords: KeywordConfig,
    client: httpx.Client | None = None,
    output_dir: Path = REPORTS_DIR,
) -> ScanResult:
    started_at = datetime.now(timezone.utc)
    selected_sources = select_sources(sources, request.sources_requested)
    selected_catalog = SourceCatalog(sources=selected_sources)

    collected_items = collect_sources(selected_catalog, request, client=client)
    enriched_items = enrich_items(
        collected_items,
        default_keywords=keywords.default_keywords,
        request_keywords=request.keywords,
        vendors=keywords.vendors,
    )
    time_filtered_items = filter_by_time(enriched_items, request, now=started_at)
    keyword_filtered_items = filter_by_keywords(time_filtered_items, request)
    deduped_items, duplicates_removed = dedupe_items(
        keyword_filtered_items,
        request.dedupe_mode,
    )
    final_items = sort_items(deduped_items, selected_sources)

    result = ScanResult(
        scan_id=str(uuid4()),
        started_at=started_at,
        ended_at=datetime.now(timezone.utc),
        range_hours=request.range_hours,
        sources_requested=request.sources_requested,
        sources_scanned=len(selected_sources),
        raw_item_count=len(collected_items),
        duplicates_removed=duplicates_removed,
        final_item_count=len(final_items),
        items=final_items,
        export_paths=[],
    )

    return export_reports(
        request=request,
        result=result,
        sources=selected_sources,
        output_dir=output_dir,
    )


def select_sources(
    catalog: SourceCatalog,
    requested_source_ids: list[str],
) -> list[SourceConfig]:
    enabled_sources = catalog.enabled_sources
    if not requested_source_ids:
        return enabled_sources

    enabled_by_id = {source.id: source for source in enabled_sources}
    unknown_sources = [source_id for source_id in requested_source_ids if source_id not in enabled_by_id]
    if unknown_sources:
        enabled_source_ids = ", ".join(source.id for source in enabled_sources) or "none"
        raise PipelineError(
            "Unknown or disabled source ID: "
            f"{', '.join(unknown_sources)}. "
            f"Enabled source IDs: {enabled_source_ids}"
        )

    selected_sources: list[SourceConfig] = []
    seen_source_ids: set[str] = set()
    for source_id in requested_source_ids:
        if source_id in seen_source_ids:
            continue
        selected_sources.append(enabled_by_id[source_id])
        seen_source_ids.add(source_id)

    return selected_sources


def enrich_items(
    items: list[CyberUpdateItem],
    default_keywords: list[str],
    request_keywords: list[str],
    vendors: list[str],
) -> list[CyberUpdateItem]:
    keyword_terms = [*default_keywords, *request_keywords]
    enriched_items: list[CyberUpdateItem] = []

    for item in items:
        searchable_text = f"{item.title} {item.description}"
        detected_cves = sorted(set([*item.cves, *extract_cves(item.title, item.description)]))
        matched_keywords = match_terms(searchable_text, keyword_terms)
        matched_vendors = sorted(set([*item.vendors_matched, *match_terms(searchable_text, vendors)]))
        category = categorize(item.title, item.description, fallback=item.category)

        enriched_items.append(
            item.model_copy(
                update={
                    "cves": detected_cves,
                    "keywords_matched": matched_keywords,
                    "vendors_matched": matched_vendors,
                    "category": category,
                }
            )
        )

    return enriched_items


def sort_items(
    items: list[CyberUpdateItem],
    sources: list[SourceConfig],
) -> list[CyberUpdateItem]:
    source_order = {source.id: index for index, source in enumerate(sources)}
    return sorted(
        items,
        key=lambda item: (
            source_order.get(item.source_id, len(source_order)),
            _sort_timestamp(item),
        ),
    )


def _sort_timestamp(item: CyberUpdateItem) -> float:
    if item.published_at is None:
        return float("inf")
    published_at = item.published_at
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    return -published_at.timestamp()
