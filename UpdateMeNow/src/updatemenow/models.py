from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceType(StrEnum):
    RSS = "rss"
    API = "api"


class ExportFormat(StrEnum):
    EXCEL = "excel"
    JSON = "json"


class DedupeMode(StrEnum):
    STRICT = "strict"
    NORMAL = "normal"
    RELAXED = "relaxed"


class SourceConfig(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    name: str
    group: str
    type: SourceType
    url: str | None = None
    provider: str | None = None
    enabled: bool = True
    default_order: int = 100

    @field_validator("id", "name", "group")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not value:
            raise ValueError("value must not be empty")
        return value


class SourceCatalog(BaseModel):
    sources: list[SourceConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_unique_source_ids(self) -> SourceCatalog:
        source_ids = [source.id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source IDs must be unique")
        return self

    @property
    def enabled_sources(self) -> list[SourceConfig]:
        return sorted(
            [source for source in self.sources if source.enabled],
            key=lambda source: source.default_order,
        )


class KeywordConfig(BaseModel):
    watchlists: dict[str, list[str]] = Field(default_factory=dict)

    @property
    def default_keywords(self) -> list[str]:
        return self.watchlists.get("default", [])

    @property
    def vendors(self) -> list[str]:
        return self.watchlists.get("vendors", [])


class ScanRequest(BaseModel):
    hours: int | None = None
    days: int | None = None
    sources_requested: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    dedupe_mode: DedupeMode = DedupeMode.NORMAL
    exports: list[ExportFormat] = Field(default_factory=lambda: [ExportFormat.EXCEL])

    @model_validator(mode="after")
    def set_default_range(self) -> ScanRequest:
        if self.hours is not None and self.days is not None:
            raise ValueError("--hours and --days cannot be used together")
        if self.hours is None and self.days is None:
            self.hours = 6
        return self

    @property
    def range_hours(self) -> int:
        if self.days is not None:
            return self.days * 24
        return self.hours or 6

    @property
    def range_label(self) -> str:
        if self.days is not None:
            unit = "day" if self.days == 1 else "days"
            return f"{self.days} {unit}"
        hours = self.hours or 6
        unit = "hour" if hours == 1 else "hours"
        return f"{hours} {unit}"


class CyberUpdateItem(BaseModel):
    id: str
    source_id: str
    source_name: str
    source_group: str
    source_type: SourceType
    published_at: datetime | None = None
    title: str
    description: str = ""
    url: str = ""
    cves: list[str] = Field(default_factory=list)
    keywords_matched: list[str] = Field(default_factory=list)
    vendors_matched: list[str] = Field(default_factory=list)
    category: str = "General"
    raw_data: dict[str, Any] = Field(default_factory=dict)
    scan_run_time: datetime


class ScanResult(BaseModel):
    scan_id: str
    started_at: datetime
    ended_at: datetime | None = None
    range_hours: int
    sources_requested: list[str] = Field(default_factory=list)
    sources_scanned: int = 0
    raw_item_count: int = 0
    duplicates_removed: int = 0
    final_item_count: int = 0
    items: list[CyberUpdateItem] = Field(default_factory=list)
    export_paths: list[str] = Field(default_factory=list)
