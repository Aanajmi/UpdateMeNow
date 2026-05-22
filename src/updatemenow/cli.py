from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
import httpx
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from updatemenow import __version__
from updatemenow.config import (
    CONFIG_DIR,
    SOURCES_FILE,
    init_config,
    load_keywords,
    load_sources,
    validate_config,
)
from updatemenow.models import DedupeMode, ExportFormat, ScanRequest, ScanResult
from updatemenow.pipeline import PipelineError, run_scan
from updatemenow.sources.collectors import CollectorError
from updatemenow.sources.health import check_source_catalog

console = Console()

app = typer.Typer(
    help="UpdateMeNow cybersecurity update reporter.",
    no_args_is_help=False,
)
config_app = typer.Typer(help="Manage UpdateMeNow configuration files.")
sources_app = typer.Typer(help="Inspect and test configured sources.")
app.add_typer(config_app, name="config")
app.add_typer(sources_app, name="sources")


def _parse_export_formats(export: str) -> list[ExportFormat]:
    formats: list[ExportFormat] = []
    for raw_part in export.split(","):
        part = raw_part.strip().lower()
        if not part:
            continue
        try:
            formats.append(ExportFormat(part))
        except ValueError as exc:
            supported = ", ".join(format.value for format in ExportFormat)
            raise typer.BadParameter(
                f"Unsupported export format '{part}'. Supported formats: {supported}."
            ) from exc

    if not formats:
        raise typer.BadParameter("At least one export format is required.")

    return formats


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", help="Show the installed UpdateMeNow version."),
    ] = False,
) -> None:
    if version:
        console.print(f"UpdateMeNow {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        scan()


@app.command()
def scan(
    hours: Annotated[
        int | None,
        typer.Option("--hours", min=1, help="Scan updates from the last N hours."),
    ] = None,
    days: Annotated[
        int | None,
        typer.Option("--days", min=1, help="Scan updates from the last N days."),
    ] = None,
    source: Annotated[
        list[str] | None,
        typer.Option("--source", help="Source ID to include. Repeat for multiple sources."),
    ] = None,
    keyword: Annotated[
        list[str] | None,
        typer.Option("--keyword", help="Keyword to match. Repeat for OR matching."),
    ] = None,
    dedupe: Annotated[
        DedupeMode,
        typer.Option(
            "--dedupe",
            case_sensitive=False,
            help="Duplicate handling mode: strict, normal, or relaxed.",
        ),
    ] = DedupeMode.NORMAL,
    export: Annotated[
        str,
        typer.Option("--export", help="Export format: excel, json, or excel,json."),
    ] = "excel",
) -> None:
    """Scan configured cybersecurity update sources."""
    try:
        request = ScanRequest(
            hours=hours,
            days=days,
            sources_requested=source or [],
            keywords=keyword or [],
            dedupe_mode=dedupe,
            exports=_parse_export_formats(export),
        )
    except ValidationError as exc:
        message = exc.errors()[0]["msg"] if exc.errors() else str(exc)
        console.print(f"[red]Invalid scan options:[/red] {message}")
        raise typer.Exit(code=2) from exc

    config_result = validate_config(allow_defaults=True)
    if not config_result.is_valid:
        console.print("[red]Config is invalid.[/red]")
        for error in config_result.errors:
            console.print(f"- {error}")
        raise typer.Exit(code=1)

    try:
        with console.status("Collecting and processing cybersecurity updates..."):
            result = run_scan(
                request=request,
                sources=load_sources(),
                keywords=load_keywords(),
            )
    except PipelineError as exc:
        console.print(f"[red]Scan failed:[/red] {exc}")
        raise typer.Exit(code=2) from exc
    except (CollectorError, httpx.HTTPError, ValueError) as exc:
        console.print(f"[red]Scan failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(_scan_summary_panel(request, result))


@config_app.command("init")
def config_init(
    config_dir: Annotated[
        Path,
        typer.Option("--config-dir", help="Directory where config files are stored."),
    ] = CONFIG_DIR,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing config files."),
    ] = False,
) -> None:
    """Create default config files."""
    result = init_config(config_dir=config_dir, overwrite=force)

    console.print("[bold cyan]UpdateMeNow config init[/bold cyan]")
    for path in result.created:
        console.print(f"[green]created[/green] {path}")
    for path in result.skipped:
        console.print(f"[yellow]skipped[/yellow] {path} already exists")

    if not result.created and result.skipped:
        console.print("Use --force to overwrite existing config files.")


@config_app.command("validate")
def config_validate(
    config_dir: Annotated[
        Path,
        typer.Option("--config-dir", help="Directory where config files are stored."),
    ] = CONFIG_DIR,
) -> None:
    """Validate config files."""
    result = validate_config(config_dir=config_dir)

    console.print("[bold cyan]UpdateMeNow config validate[/bold cyan]")
    if result.is_valid:
        console.print("[green]Config is valid.[/green]")
        console.print(f"Sources: {result.source_count}")
        console.print(f"Enabled sources: {result.enabled_source_count}")
        console.print(f"Default keywords: {result.default_keyword_count}")
        console.print(f"Vendors/products: {result.vendor_count}")
        return

    console.print("[red]Config is invalid.[/red]")
    for error in result.errors:
        console.print(f"- {error}")
    raise typer.Exit(code=1)


@sources_app.command("list")
def sources_list(
    config_dir: Annotated[
        Path,
        typer.Option("--config-dir", help="Directory where config files are stored."),
    ] = CONFIG_DIR,
) -> None:
    """List configured sources."""
    config_result = validate_config(config_dir=config_dir, allow_defaults=True)
    if not config_result.is_valid:
        console.print("[red]Config is invalid.[/red]")
        for error in config_result.errors:
            console.print(f"- {error}")
        raise typer.Exit(code=1)

    from updatemenow.config import load_sources

    sources = load_sources(config_dir / SOURCES_FILE)
    table = Table(title="UpdateMeNow Sources")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Group")
    table.add_column("Type")
    table.add_column("Enabled")
    table.add_column("Provider/URL")
    table.add_column("Order", justify="right")

    for source in sorted(sources.sources, key=lambda item: item.default_order):
        endpoint = source.provider or source.url or "-"
        enabled = "[green]yes[/green]" if source.enabled else "[yellow]no[/yellow]"
        table.add_row(
            source.id,
            source.name,
            source.group,
            source.type.value,
            enabled,
            endpoint,
            str(source.default_order),
        )

    console.print(table)


@sources_app.command("test")
def sources_test(
    config_dir: Annotated[
        Path,
        typer.Option("--config-dir", help="Directory where config files are stored."),
    ] = CONFIG_DIR,
    timeout: Annotated[
        float,
        typer.Option("--timeout", min=1.0, help="HTTP timeout in seconds per source."),
    ] = 10.0,
    include_disabled: Annotated[
        bool,
        typer.Option("--all", help="Test all configured sources, including disabled ones."),
    ] = False,
) -> None:
    """Check whether configured sources are reachable."""
    config_result = validate_config(config_dir=config_dir, allow_defaults=True)
    if not config_result.is_valid:
        console.print("[red]Config is invalid.[/red]")
        for error in config_result.errors:
            console.print(f"- {error}")
        raise typer.Exit(code=1)

    from updatemenow.config import load_sources

    sources = load_sources(config_dir / SOURCES_FILE)
    results = check_source_catalog(
        sources,
        timeout=timeout,
        include_disabled=include_disabled,
    )

    title = "UpdateMeNow Source Reachability"
    if include_disabled:
        title = "UpdateMeNow Source Reachability (All Sources)"
    table = Table(title=title)
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Type")
    table.add_column("Endpoint")
    table.add_column("Status")
    table.add_column("HTTP", justify="right")
    table.add_column("Message")

    for result in results:
        status = "[green]ok[/green]" if result.ok else "[red]failed[/red]"
        status_code = str(result.status_code) if result.status_code is not None else "-"
        table.add_row(
            result.source_id,
            result.source_type.value,
            result.endpoint or "-",
            status,
            status_code,
            result.message,
        )

    console.print(table)

    if any(not result.ok for result in results):
        raise typer.Exit(code=1)


def main() -> None:
    app()


def _scan_summary_panel(request: ScanRequest, result: ScanResult) -> Panel:
    export_labels = ", ".join(format.value for format in request.exports)
    report_lines = result.export_paths or ["No report exported."]
    source_status = f"Sources scanned: {result.sources_scanned}"
    if result.sources_failed:
        source_status = f"{source_status} ({result.sources_failed} failed; report continued)"
    warning_lines = []
    if result.source_errors:
        warning_lines = ["", "Source warnings:", *[f"- {error}" for error in result.source_errors]]
    return Panel.fit(
        "\n".join(
            [
                "UpdateMeNow Cyber Update Scan",
                f"Scan range: Last {request.range_label}",
                source_status,
                f"Raw items collected: {result.raw_item_count}",
                f"Duplicates removed: {result.duplicates_removed}",
                f"Dedupe mode: {request.dedupe_mode.value}",
                f"Final items: {result.final_item_count}",
                f"Keyword filters: {', '.join(request.keywords) or 'none'}",
                *warning_lines,
                "",
                f"Requested exports: {export_labels}",
                "Report exported:",
                *report_lines,
            ]
        ),
        border_style="cyan",
    )


if __name__ == "__main__":
    main()
