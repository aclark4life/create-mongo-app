"""End-to-end tests for scaffolding via the bundled template."""

from pathlib import Path

from typer.testing import CliRunner

from create_mongo_app.cli import app
from create_mongo_app.generate import generate, template_path

runner = CliRunner()


def test_template_is_bundled():
    root = template_path()
    assert (root / "cookiecutter.json").is_file()
    assert (root / "{{cookiecutter.project_slug}}").is_dir()
    # A dotfile must survive packaging, or generated projects break.
    assert (root / "{{cookiecutter.project_slug}}" / ".env").is_file()


def test_generate_creates_project(tmp_path: Path):
    project = generate(
        output_dir=tmp_path,
        extra_context={"project_name": "My App"},
        no_input=True,
    )
    assert project.is_dir()
    assert project.name == "my-app"  # project_slug derived from project_name
    assert (project / "backend").is_dir()
    assert (project / "docker-compose.yml").is_file()


def test_generate_applies_overrides(tmp_path: Path):
    project = generate(
        output_dir=tmp_path,
        extra_context={
            "project_name": "Overridden",
            "mongodb_database": "customdb",
        },
        no_input=True,
    )
    env = (project / ".env").read_text()
    assert "customdb" in env


def test_cli_scaffolds(tmp_path: Path):
    result = runner.invoke(
        app,
        ["cli-app", "--yes", "--directory", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "cli-app").is_dir()
    assert "Created project at" in result.output


def test_cli_bad_set_pair(tmp_path: Path):
    result = runner.invoke(
        app,
        ["x", "--yes", "--set", "novalue", "--directory", str(tmp_path)],
    )
    assert result.exit_code != 0
