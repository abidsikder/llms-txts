# ruff: noqa F401
# If the subcommand's module is not imported it will not attach itself to the cli click.group
from . import (
    beautifulsoup,
    boto3,
    commanderjs,
    devdocs,
    hy,
    icechunk,
    mlx,
    networkx,
    nodejs,
    p5js,
    progit,
    puppeteer,
    python,
    ruff,
    ty,
    typst,
    uv,
    whenever,
    xarray,
    zarr,
    zed,
)
from .cli import cli

__all__ = ["cli"]
