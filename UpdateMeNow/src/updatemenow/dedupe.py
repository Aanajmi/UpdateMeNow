from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from updatemenow.models import CyberUpdateItem, DedupeMode

WHITESPACE_PATTERN = re.compile(r"\s+")
TITLE_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
TRACKING_QUERY_NAMES = {
    "fbclid",
    "gclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "ref",
    "spm",
}
RELAXED_DUPLICATE_WINDOW_SECONDS = 48 * 60 * 60


def dedupe_items(
    items: list[CyberUpdateItem],
    mode: DedupeMode = DedupeMode.NORMAL,
) -> tuple[list[CyberUpdateItem], int]:
    seen_urls: set[str] = set()
    seen_titles_by_source: set[tuple[str, str]] = set()
    seen_titles_by_group: set[tuple[str, str]] = set()
    deduped: list[CyberUpdateItem] = []
    duplicates_removed = 0

    for item in items:
        normalized_url = canonicalize_url(item.url)
        if normalized_url:
            if normalized_url in seen_urls:
                duplicates_removed += 1
                continue
            seen_urls.add(normalized_url)

        normalized_title = normalize_title(item.title)
        title_by_source_key = (item.source_id, normalized_title)
        if normalized_title:
            if title_by_source_key in seen_titles_by_source:
                duplicates_removed += 1
                continue
            if mode != DedupeMode.STRICT:
                title_by_group_key = (item.source_group, normalized_title)
                if title_by_group_key in seen_titles_by_group:
                    duplicates_removed += 1
                    continue
            if mode == DedupeMode.RELAXED and _is_relaxed_duplicate(item, deduped):
                duplicates_removed += 1
                continue
            seen_titles_by_source.add(title_by_source_key)
            if mode != DedupeMode.STRICT:
                seen_titles_by_group.add((item.source_group, normalized_title))

        deduped.append(item)

    return deduped, duplicates_removed


def normalize_title(title: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", title.strip().casefold())


def title_signature(title: str) -> tuple[str, ...]:
    return tuple(TITLE_TOKEN_PATTERN.findall(normalize_title(title)))


def canonicalize_url(url: str) -> str:
    stripped_url = url.strip()
    if not stripped_url:
        return ""

    try:
        parts = urlsplit(stripped_url)
    except ValueError:
        return stripped_url.casefold()

    if not parts.scheme and not parts.netloc:
        return stripped_url.rstrip("/").casefold()

    query_pairs = [
        (name, value)
        for name, value in parse_qsl(parts.query, keep_blank_values=True)
        if not _is_tracking_query_param(name)
    ]
    query = urlencode(
        sorted(query_pairs, key=lambda pair: (pair[0].casefold(), pair[1])),
        doseq=True,
    )

    path = parts.path
    if path == "/":
        path = ""
    else:
        path = path.rstrip("/")

    return urlunsplit(
        (
            parts.scheme.casefold(),
            parts.netloc.casefold(),
            path,
            query,
            "",
        )
    )


def _is_tracking_query_param(name: str) -> bool:
    normalized_name = name.casefold()
    return normalized_name.startswith("utm_") or normalized_name in TRACKING_QUERY_NAMES


def _is_relaxed_duplicate(candidate: CyberUpdateItem, deduped_items: list[CyberUpdateItem]) -> bool:
    candidate_signature = title_signature(candidate.title)
    if not candidate_signature:
        return False

    candidate_tokens = set(candidate_signature)
    for kept_item in deduped_items:
        if candidate.source_id == kept_item.source_id:
            continue

        kept_signature = title_signature(kept_item.title)
        if not kept_signature:
            continue

        kept_tokens = set(kept_signature)
        overlap = candidate_tokens & kept_tokens
        smallest_signature_size = min(len(candidate_tokens), len(kept_tokens))
        if not overlap or len(overlap) / smallest_signature_size < 0.8:
            continue

        if candidate.source_group == kept_item.source_group:
            return True
        if _shares_values(candidate.cves, kept_item.cves):
            return True
        if _shares_values(candidate.vendors_matched, kept_item.vendors_matched):
            return True
        if _published_close_enough(candidate.published_at, kept_item.published_at):
            return True

    return False


def _shares_values(left: list[str], right: list[str]) -> bool:
    return bool(set(left) & set(right))


def _published_close_enough(left: datetime | None, right: datetime | None) -> bool:
    if left is None or right is None:
        return False

    left_dt = left
    right_dt = right
    if getattr(left_dt, "tzinfo", None) is None:
        left_dt = left_dt.replace(tzinfo=timezone.utc)
    else:
        left_dt = left_dt.astimezone(timezone.utc)

    if getattr(right_dt, "tzinfo", None) is None:
        right_dt = right_dt.replace(tzinfo=timezone.utc)
    else:
        right_dt = right_dt.astimezone(timezone.utc)

    return abs((left_dt - right_dt).total_seconds()) <= RELAXED_DUPLICATE_WINDOW_SECONDS
