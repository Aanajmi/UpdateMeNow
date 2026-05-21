from __future__ import annotations

from dataclasses import dataclass, field

from updatemenow.models import SourceConfig


@dataclass(frozen=True)
class SourceEndpoint:
    url: str
    params: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)


DEFAULT_HTTP_HEADERS = {
    "User-Agent": "UpdateMeNow/0.1 RSS/API checker",
}

PROVIDER_ENDPOINTS: dict[str, SourceEndpoint] = {
    "cisa_kev": SourceEndpoint(
        url="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
    ),
    "nvd": SourceEndpoint(
        url="https://services.nvd.nist.gov/rest/json/cves/2.0",
    ),
    "github_advisories": SourceEndpoint(
        url="https://api.github.com/advisories",
        headers={"Accept": "application/vnd.github+json"},
    ),
}


def resolve_source_endpoint(source: SourceConfig) -> SourceEndpoint | None:
    if source.url:
        return SourceEndpoint(url=source.url, headers={**DEFAULT_HTTP_HEADERS})
    if source.provider:
        endpoint = PROVIDER_ENDPOINTS.get(source.provider)
        if endpoint is None:
            return None
        return SourceEndpoint(
            url=endpoint.url,
            params={**endpoint.params},
            headers={**DEFAULT_HTTP_HEADERS, **endpoint.headers},
        )
    return None
