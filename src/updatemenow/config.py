from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any, Callable

from pydantic import ValidationError
import yaml

from updatemenow.models import KeywordConfig, SourceCatalog, SourceType
from updatemenow.sources.endpoints import PROVIDER_ENDPOINTS

CONFIG_DIR = Path("config")
SOURCES_FILE = "sources.yaml"
KEYWORDS_FILE = "keywords.yaml"
DEFAULTS_PACKAGE = "updatemenow.defaults"


def _load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}.")

    return data


def _load_default_yaml(filename: str) -> dict[str, Any]:
    resource = files(DEFAULTS_PACKAGE).joinpath(filename)
    data = yaml.safe_load(resource.read_text(encoding="utf-8")) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in packaged default {filename}.")

    return data


def _read_default_text(filename: str) -> str:
    return files(DEFAULTS_PACKAGE).joinpath(filename).read_text(encoding="utf-8")


def _format_validation_error(error: ValidationError) -> list[str]:
    messages: list[str] = []
    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"])
        messages.append(f"{location}: {detail['msg']}")
    return messages


class ConfigInitResult:
    def __init__(self, created: list[Path], skipped: list[Path]) -> None:
        self.created = created
        self.skipped = skipped


class ConfigValidationResult:
    def __init__(
        self,
        errors: list[str],
        source_count: int = 0,
        enabled_source_count: int = 0,
        default_keyword_count: int = 0,
        vendor_count: int = 0,
    ) -> None:
        self.errors = errors
        self.source_count = source_count
        self.enabled_source_count = enabled_source_count
        self.default_keyword_count = default_keyword_count
        self.vendor_count = vendor_count

    @property
    def is_valid(self) -> bool:
        return not self.errors


def init_config(config_dir: Path = CONFIG_DIR, overwrite: bool = False) -> ConfigInitResult:
    config_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    skipped: list[Path] = []

    for filename in (SOURCES_FILE, KEYWORDS_FILE):
        target = config_dir / filename
        if target.exists() and not overwrite:
            skipped.append(target)
            continue

        target.write_text(_read_default_text(filename), encoding="utf-8")
        created.append(target)

    return ConfigInitResult(created=created, skipped=skipped)


def validate_config(
    config_dir: Path = CONFIG_DIR,
    *,
    allow_defaults: bool = False,
) -> ConfigValidationResult:
    errors: list[str] = []
    source_count = 0
    enabled_source_count = 0
    default_keyword_count = 0
    vendor_count = 0

    sources_path = config_dir / SOURCES_FILE
    if not sources_path.exists():
        if allow_defaults:
            source_count, enabled_source_count, source_errors = _validate_sources_config(
                lambda: _load_default_yaml(SOURCES_FILE),
                f"packaged default {SOURCES_FILE}",
            )
            errors.extend(source_errors)
        else:
            errors.append(f"Missing config file: {sources_path}")
    else:
        source_count, enabled_source_count, source_errors = _validate_sources_config(
            lambda: _load_yaml_file(sources_path),
            str(sources_path),
        )
        errors.extend(source_errors)

    keywords_path = config_dir / KEYWORDS_FILE
    if not keywords_path.exists():
        if allow_defaults:
            default_keyword_count, vendor_count, keyword_errors = _validate_keywords_config(
                lambda: _load_default_yaml(KEYWORDS_FILE),
                f"packaged default {KEYWORDS_FILE}",
            )
            errors.extend(keyword_errors)
        else:
            errors.append(f"Missing config file: {keywords_path}")
    else:
        default_keyword_count, vendor_count, keyword_errors = _validate_keywords_config(
            lambda: _load_yaml_file(keywords_path),
            str(keywords_path),
        )
        errors.extend(keyword_errors)

    return ConfigValidationResult(
        errors=errors,
        source_count=source_count,
        enabled_source_count=enabled_source_count,
        default_keyword_count=default_keyword_count,
        vendor_count=vendor_count,
    )


def _validate_sources_config(
    load_data: Callable[[], dict[str, Any]],
    label: str,
) -> tuple[int, int, list[str]]:
    try:
        sources = SourceCatalog.model_validate(load_data())
        return (
            len(sources.sources),
            len(sources.enabled_sources),
            _validate_sources_for_runtime(label, sources),
        )
    except yaml.YAMLError as exc:
        return 0, 0, [f"{label}: invalid YAML: {exc}"]
    except ValidationError as exc:
        return 0, 0, [f"{label}: {message}" for message in _format_validation_error(exc)]
    except ValueError as exc:
        return 0, 0, [f"{label}: {exc}"]


def _validate_keywords_config(
    load_data: Callable[[], dict[str, Any]],
    label: str,
) -> tuple[int, int, list[str]]:
    try:
        keywords = KeywordConfig.model_validate(load_data())
        return (
            len(keywords.default_keywords),
            len(keywords.vendors),
            _validate_keyword_watchlists(label, keywords),
        )
    except yaml.YAMLError as exc:
        return 0, 0, [f"{label}: invalid YAML: {exc}"]
    except ValidationError as exc:
        return 0, 0, [f"{label}: {message}" for message in _format_validation_error(exc)]
    except ValueError as exc:
        return 0, 0, [f"{label}: {exc}"]


def _validate_sources_for_runtime(path: Path | str, sources: SourceCatalog) -> list[str]:
    errors: list[str] = []
    for source in sources.sources:
        if not source.enabled:
            continue
        if not source.url and not source.provider:
            errors.append(f"{path}: enabled source '{source.id}' needs url or provider")
        if source.type == SourceType.RSS and not source.url:
            errors.append(f"{path}: RSS source '{source.id}' needs url")
        if source.type == SourceType.API and not source.provider:
            errors.append(f"{path}: API source '{source.id}' needs provider")
        if (
            source.type == SourceType.API
            and source.provider
            and source.provider not in PROVIDER_ENDPOINTS
        ):
            errors.append(
                f"{path}: API source '{source.id}' uses unknown provider '{source.provider}'"
            )
    return errors


def _validate_keyword_watchlists(path: Path | str, keywords: KeywordConfig) -> list[str]:
    errors: list[str] = []
    for name in ("default", "vendors"):
        values = keywords.watchlists.get(name)
        if values is None:
            errors.append(f"{path}: missing watchlists.{name}")
        elif not values:
            errors.append(f"{path}: watchlists.{name} must not be empty")
    return errors


def load_default_sources() -> SourceCatalog:
    return SourceCatalog.model_validate(_load_default_yaml(SOURCES_FILE))


def load_default_keywords() -> KeywordConfig:
    return KeywordConfig.model_validate(_load_default_yaml(KEYWORDS_FILE))


def load_sources(path: Path | None = None) -> SourceCatalog:
    resolved_path = path or CONFIG_DIR / SOURCES_FILE
    data = _load_yaml_file(resolved_path) if resolved_path.exists() else _load_default_yaml(SOURCES_FILE)
    return SourceCatalog.model_validate(data)


def load_keywords(path: Path | None = None) -> KeywordConfig:
    resolved_path = path or CONFIG_DIR / KEYWORDS_FILE
    data = _load_yaml_file(resolved_path) if resolved_path.exists() else _load_default_yaml(KEYWORDS_FILE)
    return KeywordConfig.model_validate(data)
