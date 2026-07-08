"""``create-mongo-app`` command line interface.

Usage mirrors create-react-app: the primary argument is the project name.

    create-mongo-app my-app

By default this prompts for the remaining template values (like ``cookiecutter``
does). Pass ``--yes`` to accept all defaults non-interactively, and use
``--set key=value`` to override individual template variables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from . import __version__
from .generate import generate

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Scaffold a full-stack FastAPI + MongoDB application.",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"create-mongo-app {__version__}")
        raise typer.Exit()


def _parse_set(values: list[str]) -> dict[str, str]:
    """Parse ``--set key=value`` pairs into template context overrides."""
    context: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise typer.BadParameter(
                f"--set expects key=value, got {item!r}", param_hint="--set"
            )
        key, _, val = item.partition("=")
        key = key.strip()
        if not key:
            raise typer.BadParameter("--set key must not be empty", param_hint="--set")
        context[key] = val
    return context


@app.command()
def main(
    project_name: Optional[str] = typer.Argument(
        None,
        help="Name of the project to create (also used as the directory name).",
    ),
    directory: Path = typer.Option(
        Path("."),
        "--directory",
        "-d",
        help="Parent directory the project is created inside.",
        file_okay=False,
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Accept all template defaults without prompting.",
    ),
    set_: list[str] = typer.Option(
        [],
        "--set",
        "-s",
        metavar="KEY=VALUE",
        help="Override a template variable (repeatable).",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite the target project directory if it already exists.",
    ),
    _version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """Create a new FastAPI + MongoDB project."""
    extra_context = _parse_set(set_)
    if project_name:
        extra_context.setdefault("project_name", project_name)

    try:
        project_dir = generate(
            output_dir=directory,
            extra_context=extra_context,
            # Prompt for the remaining values unless --yes was given. Values in
            # extra_context prefill the prompt defaults (or are used directly
            # when no_input is True).
            no_input=yes,
            overwrite=overwrite,
        )
    except Exception as exc:  # cookiecutter raises many subclasses
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.secho(f"\nCreated project at {project_dir}", fg=typer.colors.GREEN)
    typer.echo("\nNext steps:")
    typer.echo(f"  cd {project_dir.name}")
    typer.echo("  docker compose up -d       # start MongoDB + backend + frontend")
    typer.echo("  # or run the backend directly:")
    typer.echo("  cd backend/app && pip install -r requirements.txt && uvicorn app.main:app --reload")


if __name__ == "__main__":
    app()
