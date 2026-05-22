from __future__ import annotations

from datetime import datetime, timezone

import httpx

from updatemenow.models import CyberUpdateItem, ScanRequest, SourceConfig
from updatemenow.sources._items import parse_datetime, stable_item_id
from updatemenow.sources.endpoints import resolve_source_endpoint


class GitHubAdvisoriesCollector:
    def __init__(self, source: SourceConfig, client: httpx.Client | None = None) -> None:
        self.source = source
        self.client = client

    def collect(self, request: ScanRequest) -> list[CyberUpdateItem]:
        endpoint = resolve_source_endpoint(self.source)
        if endpoint is None:
            raise ValueError(f"GitHub advisories source '{self.source.id}' has no endpoint.")

        params = {
            **endpoint.params,
            "per_page": "100",
            "sort": "published",
            "direction": "desc",
        }

        if self.client is not None:
            return self._collect_with_client(self.client, endpoint.url, params, endpoint.headers)

        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            return self._collect_with_client(client, endpoint.url, params, endpoint.headers)

    def _collect_with_client(
        self,
        client: httpx.Client,
        url: str,
        params: dict[str, str],
        headers: dict[str, str],
    ) -> list[CyberUpdateItem]:
        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        scan_run_time = datetime.now(timezone.utc)
        return [self._advisory_to_item(record, scan_run_time) for record in data]

    def _advisory_to_item(
        self,
        record: dict,
        scan_run_time: datetime,
    ) -> CyberUpdateItem:
        advisory_id = str(record.get("ghsa_id") or record.get("id") or "").strip()
        title = str(record.get("summary", "")).strip() or advisory_id
        description = str(record.get("description", "")).strip()
        url = str(record.get("html_url") or record.get("url") or "").strip()
        cve_id = str(record.get("cve_id") or "").strip()

        return CyberUpdateItem(
            id=stable_item_id(self.source.id, advisory_id or url or title),
            source_id=self.source.id,
            source_name=self.source.name,
            source_group=self.source.group,
            source_type=self.source.type,
            published_at=parse_datetime(record.get("published_at")),
            title=title,
            description=description,
            url=url,
            cves=[cve_id] if cve_id.startswith("CVE-") else [],
            category="Vendor Advisory",
            raw_data=record,
            scan_run_time=scan_run_time,
        )
