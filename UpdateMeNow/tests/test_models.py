import pytest
from pydantic import ValidationError

from updatemenow.models import ExportFormat, ScanRequest, SourceCatalog


def test_scan_request_defaults_to_six_hours_and_excel() -> None:
    request = ScanRequest()

    assert request.range_hours == 6
    assert request.range_label == "6 hours"
    assert request.exports == [ExportFormat.EXCEL]


def test_scan_request_days_to_hours() -> None:
    request = ScanRequest(days=7)

    assert request.range_hours == 168
    assert request.range_label == "7 days"


def test_source_catalog_rejects_duplicate_ids() -> None:
    with pytest.raises(ValidationError):
        SourceCatalog.model_validate(
            {
                "sources": [
                    {
                        "id": "nvd",
                        "name": "NVD",
                        "group": "vulnerability_database",
                        "type": "api",
                        "provider": "nvd",
                    },
                    {
                        "id": "nvd",
                        "name": "Duplicate NVD",
                        "group": "vulnerability_database",
                        "type": "api",
                        "provider": "nvd",
                    },
                ]
            }
        )

