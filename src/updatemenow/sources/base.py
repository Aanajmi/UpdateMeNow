from __future__ import annotations

from typing import Protocol

from updatemenow.models import CyberUpdateItem, ScanRequest, SourceConfig


class SourceCollector(Protocol):
    source: SourceConfig

    def collect(self, request: ScanRequest) -> list[CyberUpdateItem]:
        """Collect normalized update items for a scan request."""

