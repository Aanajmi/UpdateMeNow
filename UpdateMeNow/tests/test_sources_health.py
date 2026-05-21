import httpx

from updatemenow.config import load_default_sources
from updatemenow.models import SourceCatalog, SourceConfig, SourceType
from updatemenow.sources.health import check_source_catalog, resolve_source_endpoint


def test_resolve_known_provider_endpoint() -> None:
    source = SourceConfig(
        id="nvd",
        name="NVD CVEs",
        group="vulnerability_database",
        type=SourceType.API,
        provider="nvd",
    )

    endpoint = resolve_source_endpoint(source)

    assert endpoint is not None
    assert endpoint.url == "https://services.nvd.nist.gov/rest/json/cves/2.0"
    assert endpoint.params == {}


def test_source_catalog_health_uses_httpx_client() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=request, json={})

    catalog = load_default_sources()
    client = httpx.Client(transport=httpx.MockTransport(handler))

    results = check_source_catalog(catalog, client=client)

    assert len(results) == len(catalog.enabled_sources)
    assert all(result.ok for result in results)
    assert {result.status_code for result in results} == {200}


def test_source_catalog_health_reports_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, request=request)

    catalog = load_default_sources()
    client = httpx.Client(transport=httpx.MockTransport(handler))

    results = check_source_catalog(catalog, client=client)

    assert len(results) == len(catalog.enabled_sources)
    assert all(not result.ok for result in results)
    assert {result.status_code for result in results} == {503}


def test_source_catalog_health_can_include_disabled_sources() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=request, json={})

    catalog = SourceCatalog(
        sources=[
            SourceConfig(
                id="enabled",
                name="Enabled",
                group="government",
                type=SourceType.RSS,
                url="https://example.com/enabled.xml",
                enabled=True,
                default_order=20,
            ),
            SourceConfig(
                id="disabled",
                name="Disabled",
                group="government",
                type=SourceType.RSS,
                url="https://example.com/disabled.xml",
                enabled=False,
                default_order=10,
            ),
        ]
    )
    client = httpx.Client(transport=httpx.MockTransport(handler))

    results = check_source_catalog(catalog, client=client, include_disabled=True)

    assert [result.source_id for result in results] == ["disabled", "enabled"]
