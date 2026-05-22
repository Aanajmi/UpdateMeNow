from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx

from updatemenow.models import CyberUpdateItem, ScanRequest, SourceConfig
from updatemenow.sources._items import parse_datetime, stable_item_id, truncate_text
from updatemenow.sources.endpoints import resolve_source_endpoint


class NVDCollector:
    def __init__(self, source: SourceConfig, client: httpx.Client | None = None) -> None:
        self.source = source
        self.client = client

    def collect(self, request: ScanRequest) -> list[CyberUpdateItem]:
        endpoint = resolve_source_endpoint(self.source)
        if endpoint is None:
            raise ValueError(f"NVD source '{self.source.id}' has no endpoint.")

        params = {
            **endpoint.params,
            **_range_params(request),
            "resultsPerPage": "100",
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
        return [
            self._vulnerability_to_item(record, scan_run_time)
            for record in data.get("vulnerabilities", [])
        ]

    def _vulnerability_to_item(
        self,
        record: dict,
        scan_run_time: datetime,
    ) -> CyberUpdateItem:
        cve = record.get("cve", {})
        cve_id = cve.get("id", "unknown-cve")
        description = _english_description(cve.get("descriptions", []))
        title = f"{cve_id}: {truncate_text(description)}" if description else cve_id
        published_at = parse_datetime(cve.get("published"))
        url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"

        return CyberUpdateItem(
            id=stable_item_id(self.source.id, cve_id),
            source_id=self.source.id,
            source_name=self.source.name,
            source_group=self.source.group,
            source_type=self.source.type,
            published_at=published_at,
            title=title,
            description=description,
            url=url,
            cves=[cve_id] if cve_id.startswith("CVE-") else [],
            category="Vulnerability",
            raw_data=record,
            scan_run_time=scan_run_time,
        )


def _range_params(request: ScanRequest) -> dict[str, str]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=request.range_hours)
    return {
        "pubStartDate": _nvd_datetime(start),
        "pubEndDate": _nvd_datetime(end),
    }


def _nvd_datetime(value: datetime) -> str:
    utc_value = value.astimezone(timezone.utc)
    return utc_value.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _english_description(descriptions: list[dict]) -> str:
    for description in descriptions:
        if description.get("lang") == "en":
            return str(description.get("value", "")).strip()
    if descriptions:
        return str(descriptions[0].get("value", "")).strip()
    return ""
