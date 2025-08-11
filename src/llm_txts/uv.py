import logging

import click

from .cli import cli, collect, dl_tgz, gh_latest_tag
from .license_info import license_info


@click.command()
@click.pass_context
def uv(ctx):
    scratchspace = ctx.obj["scratchspace"] / "uv"
    scratchspace.mkdir(exist_ok=True)

    logging.info("Finding latest version of uv")
    version = gh_latest_tag("astral-sh/uv")

    logging.info(f"Downloading uv {version} source code from github")
    download_url = f"https://github.com/astral-sh/uv/archive/refs/tags/{version}.tar.gz"

    dl_tgz(download_url, scratchspace)
    extracted_dest = scratchspace / f"uv-{version}"
    logging.info(f"Wrote source code to {extracted_dest}")

    txts = ctx.obj["txts"]
    txt_dest = txts / f"uv-{version}.md"
    logging.info(f"Collecting uv md docs together and writing to {txt_dest}")
    collect("**.md", extracted_dest / "docs", txt_dest, exclude="cli.md")

    logging.info(f"Done with uv {version}")


license_info["uv"] = "MIT License"
cli.add_command(uv)
