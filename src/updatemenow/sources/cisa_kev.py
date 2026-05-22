from __future__ import annotations

from datetime import datetime, timezone

import httpx

from updatemenow.models import CyberUpdateItem, ScanRequest, SourceConfig
from updatemenow.sources._items import parse_date, stable_item_id
from updatemenow.sources.endpoints import resolve_source_endpoint


class CISAKEVCollector:
    def __init__(self, source: SourceConfig, client: httpx.Client | None = None) -> None:
        self.source = source
        self.client = client

    def collect(self, request: ScanRequest) -> list[CyberUpdateItem]:
        endpoint = resolve_source_endpoint(self.source)
        if endpoint is None:
            raise ValueError(f"CISA KEV source '{self.source.id}' has no endpoint.")

        if self.client is not None:
            return self._collect_with_client(self.client, endpoint.url, endpoint.headers)

        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            return self._collect_with_client(client, endpoint.url, endpoint.headers)

    def _collect_with_client(
        self,
        client: httpx.Client,
        url: str,
        headers: dict[str, str],
    ) -> list[CyberUpdateItem]:
        response = client.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        scan_run_time = datetime.now(timezone.utc)
        return [
            self._vulnerability_to_item(record, scan_run_time)
            for record in data.get("vulnerabilities", [])
        ]

    def _vulnerability_to_item(
        self,
        record: dict,
        scan_run_time: datetime,
    ) -> CyberUpdateItem:
        cve_id = str(record.get("cveID", "")).strip()
        vendor = str(record.get("vendorProject", "")).strip()
        product = str(record.get("product", "")).strip()
        title = str(record.get("vulnerabilityName", "")).strip() or cve_id
        description = str(record.get("shortDescription", "")).strip()
        notes = str(record.get("notes", "")).strip()

        return CyberUpdateItem(
            id=stable_item_id(self.source.id, cve_id or title),
            source_id=self.source.id,
            source_name=self.source.name,
            source_group=self.source.group,
            source_type=self.source.type,
            published_at=parse_date(record.get("dateAdded")),
            title=title,
            description=description,
            url=notes,
            cves=[cve_id] if cve_id.startswith("CVE-") else [],
            vendors_matched=[value for value in (vendor, product) if value],
            category="Exploited Vulnerability",
            raw_data=record,
            scan_run_time=scan_run_time,
        )
