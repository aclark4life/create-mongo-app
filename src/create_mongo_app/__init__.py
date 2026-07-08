"""create-mongo-app: scaffold a full-stack FastAPI + MongoDB application."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("create-mongo-app")
except PackageNotFoundError:  # running from a source checkout without install
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
