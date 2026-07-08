"""Drive the bundled cookiecutter template programmatically.

The FastAPI + MongoDB template is vendored under ``template/`` as package data
(a standard cookiecutter layout: ``cookiecutter.json`` + the
``{{cookiecutter.project_slug}}`` payload + ``hooks/``). We locate it via
``importlib.resources`` so it works whether the package is installed as a
wheel, an editable install, or run from a source checkout.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from cookiecutter.main import cookiecutter

TEMPLATE_PACKAGE = "create_mongo_app"
TEMPLATE_DIRNAME = "template"


def template_path() -> Path:
    """Return the on-disk path to the bundled cookiecutter template."""
    root = resources.files(TEMPLATE_PACKAGE) / TEMPLATE_DIRNAME
    # resources.files can return a non-filesystem Traversable for zipped
    # installs; cookiecutter needs a real path. as_file materializes it, but
    # for our normal (unzipped) installs the path already exists directly.
    if isinstance(root, Path):
        return root
    with resources.as_file(root) as p:
        return p


def generate(
    *,
    output_dir: Path,
    extra_context: dict[str, str] | None = None,
    no_input: bool = False,
    overwrite: bool = False,
) -> Path:
    """Render the bundled template into ``output_dir``.

    Parameters
    ----------
    output_dir:
        Directory the generated project directory is created inside.
    extra_context:
        Values that override the template's ``cookiecutter.json`` defaults
        (e.g. ``{"project_name": "My App"}``). Anything not supplied is either
        prompted for (interactive) or defaulted (``no_input=True``).
    no_input:
        Skip all prompts and use defaults / ``extra_context``.
    overwrite:
        Overwrite an existing target project directory if it exists.

    Returns
    -------
    Path to the generated project directory.
    """
    result = cookiecutter(
        str(template_path()),
        no_input=no_input,
        extra_context=extra_context or {},
        output_dir=str(output_dir),
        overwrite_if_exists=overwrite,
    )
    return Path(result)
