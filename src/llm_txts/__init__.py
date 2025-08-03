# If the subcommand's module is not imported it will not attach itself to the cli click.group
from . import devdocs, icechunk, mlx, progit, python, ruff, uv, xarray, zarr, zed
from .cli import cli

__all__ = ["cli"]
