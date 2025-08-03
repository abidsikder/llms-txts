# If the subcommand's module is not imported it will not attach itself to the cli click.group
from . import astral_sh, devdocs, icechunk, mlx, progit, python, xarray, zarr, zed
from .cli import cli

__all__ = ["cli"]
