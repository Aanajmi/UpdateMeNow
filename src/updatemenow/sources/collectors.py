from __future__ import annotations

import httpx

from updatemenow.models import CyberUpdateItem, ScanRequest, SourceCatalog, SourceConfig, SourceType
from updatemenow.sources.base import SourceCollector
from updatemenow.sources.cisa_kev import CISAKEVCollector
from updatemenow.sources.github import GitHubAdvisoriesCollector
from updatemenow.sources.nvd import NVDCollector
from updatemenow.sources.rss import RSSCollector


class CollectorError(RuntimeError):
    pass


def build_collector(
    source: SourceConfig,
    client: httpx.Client | None = None,
) -> SourceCollector:
    if source.type == SourceType.RSS:
        return RSSCollector(source=source, client=client)

    if source.provider == "cisa_kev":
        return CISAKEVCollector(source=source, client=client)
    if source.provider == "nvd":
        return NVDCollector(source=source, client=client)
    if source.provider == "github_advisories":
        return GitHubAdvisoriesCollector(source=source, client=client)

    raise CollectorError(f"No collector exists for source '{source.id}'.")


def collect_sources(
    catalog: SourceCatalog,
    request: ScanRequest,
    client: httpx.Client | None = None,
) -> tuple[list[CyberUpdateItem], list[str]]:
    requested = set(request.sources_requested)
    sources = [
        source
        for source in catalog.enabled_sources
        if not requested or source.id in requested
    ]

    items: list[CyberUpdateItem] = []
    errors: list[str] = []
    for source in sources:
        try:
            collector = build_collector(source, client=client)
            items.extend(collector.collect(request))
        except (CollectorError, httpx.HTTPError, ValueError) as exc:
            errors.append(f"{source.id}: {exc}")
    return items, errors
