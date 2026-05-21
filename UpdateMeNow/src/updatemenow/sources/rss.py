from __future__ import annotations

import calendar
from datetime import datetime, timezone
from typing import Any

import feedparser
import httpx

from updatemenow.models import CyberUpdateItem, ScanRequest, SourceConfig
from updatemenow.sources._items import stable_item_id
from updatemenow.sources.endpoints import DEFAULT_HTTP_HEADERS


class RSSCollector:
    def __init__(self, source: SourceConfig, client: httpx.Client | None = None) -> None:
        self.source = source
        self.client = client

    def collect(self, request: ScanRequest) -> list[CyberUpdateItem]:
        if not self.source.url:
            raise ValueError(f"RSS source '{self.source.id}' requires a URL.")

        if self.client is not None:
            return self._collect_with_client(self.client)

        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            return self._collect_with_client(client)

    def _collect_with_client(self, client: httpx.Client) -> list[CyberUpdateItem]:
        response = client.get(self.source.url, headers=DEFAULT_HTTP_HEADERS)
        response.raise_for_status()

        parsed_feed = feedparser.parse(response.content)
        scan_run_time = datetime.now(timezone.utc)

        return [self._entry_to_item(entry, scan_run_time) for entry in parsed_feed.entries]

    def _entry_to_item(self, entry: Any, scan_run_time: datetime) -> CyberUpdateItem:
        title = str(entry.get("title", "")).strip() or "Untitled RSS item"
        url = str(entry.get("link", "")).strip()
        description = str(entry.get("summary", entry.get("description", ""))).strip()
        published_at = _entry_datetime(entry)
        identity = url or title

        return CyberUpdateItem(
            id=stable_item_id(self.source.id, identity),
            source_id=self.source.id,
            source_name=self.source.name,
            source_group=self.source.group,
            source_type=self.source.type,
            published_at=published_at,
            title=title,
            description=description,
            url=url,
            raw_data=dict(entry),
            scan_run_time=scan_run_time,
        )


def _entry_datetime(entry: Any) -> datetime | None:
    parsed_time = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed_time is None:
        return None
    timestamp = calendar.timegm(parsed_time)
    return datetime.fromtimestamp(timestamp, timezone.utc)
