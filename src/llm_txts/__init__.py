# ruff: noqa F401
# If the subcommand's module is not imported it will not attach itself to the cli click.group
from . import (
    boto3,
    beautifulsoup,
    commanderjs,
    devdocs,
    icechunk,
    mlx,
    nodejs,
    progit,
    python,
    ruff,
    hy,
    puppeteer,
    ty,
    networkx,
    typst,
    uv,
    xarray,
    whenever,
    zarr,
    zed,
)
from .cli import cli

__all__ = ["cli"]
