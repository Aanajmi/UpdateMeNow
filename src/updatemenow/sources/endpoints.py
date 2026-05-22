from __future__ import annotations

from dataclasses import dataclass, field

from updatemenow.models import SourceConfig


@dataclass(frozen=True)
class SourceEndpoint:
    url: str
    params: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)


DEFAULT_HTTP_HEADERS = {
    # Some public cybersecurity feeds, especially CISA, block bare Python
    # clients or unknown command-line user agents with HTTP 403.  Use a
    # normal browser-like header set so the tool works on fresh machines too.
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36 UpdateMeNow/1.0"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, application/json, text/html;q=0.9, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
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
