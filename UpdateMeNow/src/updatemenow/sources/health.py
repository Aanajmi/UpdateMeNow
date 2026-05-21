from __future__ import annotations

from dataclasses import dataclass

import httpx

from updatemenow.models import SourceCatalog, SourceConfig, SourceType
from updatemenow.sources.endpoints import resolve_source_endpoint


@dataclass(frozen=True)
class SourceCheckResult:
    source_id: str
    source_type: SourceType
    endpoint: str | None
    ok: bool
    message: str
    status_code: int | None = None


def check_source_catalog(
    catalog: SourceCatalog,
    timeout: float = 10.0,
    client: httpx.Client | None = None,
    include_disabled: bool = False,
) -> list[SourceCheckResult]:
    sources = _sources_to_check(catalog, include_disabled=include_disabled)
    if client is not None:
        return [_test_source(source, client) for source in sources]

    with httpx.Client(timeout=timeout, follow_redirects=True) as managed_client:
        return [_test_source(source, managed_client) for source in sources]


def _sources_to_check(
    catalog: SourceCatalog,
    include_disabled: bool,
) -> list[SourceConfig]:
    if include_disabled:
        return sorted(catalog.sources, key=lambda source: source.default_order)
    return catalog.enabled_sources


def _test_source(source: SourceConfig, client: httpx.Client) -> SourceCheckResult:
    endpoint = resolve_source_endpoint(source)
    if endpoint is None:
        return SourceCheckResult(
            source_id=source.id,
            source_type=source.type,
            endpoint=None,
            ok=False,
            message="No URL or known provider endpoint configured.",
        )

    try:
        params = _health_params(source, endpoint.params)
        response = client.get(
            endpoint.url,
            params=params,
            headers=endpoint.headers,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return SourceCheckResult(
            source_id=source.id,
            source_type=source.type,
            endpoint=endpoint.url,
            ok=False,
            message=exc.response.reason_phrase,
            status_code=exc.response.status_code,
        )
    except httpx.HTTPError as exc:
        return SourceCheckResult(
            source_id=source.id,
            source_type=source.type,
            endpoint=endpoint.url,
            ok=False,
            message=str(exc),
        )

    return SourceCheckResult(
        source_id=source.id,
        source_type=source.type,
        endpoint=endpoint.url,
        ok=True,
        message="Reachable.",
        status_code=response.status_code,
    )


def _health_params(source: SourceConfig, params: dict[str, str]) -> dict[str, str]:
    if source.provider == "nvd":
        return {**params, "resultsPerPage": "1"}
    if source.provider == "github_advisories":
        return {**params, "per_page": "1"}
    return params
