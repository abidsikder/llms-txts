# ruff: noqa F401
# If the subcommand's module is not imported it will not attach itself to the cli click.group
from . import (
    boto3,
    beautifulsoup,
    devdocs,
    icechunk,
    mlx,
    progit,
    python,
    ruff,
    ty,
    typst,
    uv,
    xarray,
    zarr,
    zed,
)
from .cli import cli

__all__ = ["cli"]
