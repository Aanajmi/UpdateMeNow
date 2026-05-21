import httpx
import pytest

from updatemenow.config import load_default_sources
from updatemenow.models import ScanRequest, SourceConfig, SourceType
from updatemenow.sources.collectors import CollectorError, build_collector, collect_sources
from updatemenow.sources.cisa_kev import CISAKEVCollector
from updatemenow.sources.github import GitHubAdvisoriesCollector
from updatemenow.sources.nvd import NVDCollector
from updatemenow.sources.rss import RSSCollector


def test_rss_collector_normalizes_feed_items() -> None:
    rss_body = """<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
      <channel>
        <title>Security Feed</title>
        <item>
          <title>Example advisory</title>
          <link>https://example.com/advisory</link>
          <description>Example description</description>
          <pubDate>Wed, 20 May 2026 14:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=request, text=rss_body)

    source = SourceConfig(
        id="example_rss",
        name="Example RSS",
        group="security_news",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
    )
    collector = RSSCollector(source=source, client=httpx.Client(transport=httpx.MockTransport(handler)))

    items = collector.collect(ScanRequest())

    assert len(items) == 1
    assert items[0].source_id == "example_rss"
    assert items[0].title == "Example advisory"
    assert items[0].url == "https://example.com/advisory"
    assert items[0].published_at is not None


def test_nvd_collector_normalizes_cve_records() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "pubStartDate" in request.url.params
        assert "pubEndDate" in request.url.params
        assert request.url.params["resultsPerPage"] == "100"
        return httpx.Response(
            200,
            request=request,
            json={
                "vulnerabilities": [
                    {
                        "cve": {
                            "id": "CVE-2026-12345",
                            "published": "2026-05-20T12:00:00.000",
                            "descriptions": [
                                {
                                    "lang": "en",
                                    "value": "A test vulnerability in a product.",
                                }
                            ],
                        }
                    }
                ]
            },
        )

    source = _source("nvd", "NVD CVEs", "nvd")
    collector = NVDCollector(source=source, client=httpx.Client(transport=httpx.MockTransport(handler)))

    items = collector.collect(ScanRequest(hours=6))

    assert len(items) == 1
    assert items[0].title.startswith("CVE-2026-12345")
    assert items[0].cves == ["CVE-2026-12345"]
    assert items[0].category == "Vulnerability"
    assert items[0].url == "https://nvd.nist.gov/vuln/detail/CVE-2026-12345"


def test_cisa_kev_collector_normalizes_catalog_records() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            request=request,
            json={
                "vulnerabilities": [
                    {
                        "cveID": "CVE-2026-22222",
                        "vendorProject": "Example Vendor",
                        "product": "Example Product",
                        "vulnerabilityName": "Example Exploited Vulnerability",
                        "dateAdded": "2026-05-20",
                        "shortDescription": "Known exploited test vulnerability.",
                        "notes": "https://example.com/vendor-advisory",
                    }
                ]
            },
        )

    source = _source("cisa_kev", "CISA Known Exploited Vulnerabilities", "cisa_kev")
    collector = CISAKEVCollector(source=source, client=httpx.Client(transport=httpx.MockTransport(handler)))

    items = collector.collect(ScanRequest())

    assert len(items) == 1
    assert items[0].cves == ["CVE-2026-22222"]
    assert items[0].vendors_matched == ["Example Vendor", "Example Product"]
    assert items[0].category == "Exploited Vulnerability"
    assert items[0].url == "https://example.com/vendor-advisory"


def test_github_advisories_collector_normalizes_advisories() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["accept"] == "application/vnd.github+json"
        assert request.url.params["per_page"] == "100"
        assert request.url.params["sort"] == "published"
        return httpx.Response(
            200,
            request=request,
            json=[
                {
                    "ghsa_id": "GHSA-abcd-1234-efgh",
                    "cve_id": "CVE-2026-33333",
                    "summary": "Example GitHub advisory",
                    "description": "GitHub advisory description.",
                    "html_url": "https://github.com/advisories/GHSA-abcd-1234-efgh",
                    "published_at": "2026-05-20T13:00:00Z",
                }
            ],
        )

    source = _source("github", "GitHub Security Advisories", "github_advisories")
    collector = GitHubAdvisoriesCollector(
        source=source,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    items = collector.collect(ScanRequest())

    assert len(items) == 1
    assert items[0].title == "Example GitHub advisory"
    assert items[0].cves == ["CVE-2026-33333"]
    assert items[0].category == "Vendor Advisory"


def test_collect_sources_honors_source_filter() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "services.nvd.nist.gov"
        return httpx.Response(200, request=request, json={"vulnerabilities": []})

    catalog = load_default_sources()
    client = httpx.Client(transport=httpx.MockTransport(handler))

    items = collect_sources(catalog, ScanRequest(sources_requested=["nvd"]), client=client)

    assert items == []


def test_build_collector_rejects_unknown_provider() -> None:
    source = _source("unknown", "Unknown", "unknown_provider")

    with pytest.raises(CollectorError):
        build_collector(source)


def _source(source_id: str, name: str, provider: str) -> SourceConfig:
    return SourceConfig(
        id=source_id,
        name=name,
        group="vulnerability_database",
        type=SourceType.API,
        provider=provider,
    )
