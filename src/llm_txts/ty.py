import logging

import click

from .cli import cli, collect, dl_tgz
from .license_info import license_info


@click.command()
@click.pass_context
def ty(ctx):
    scratchspace = ctx.obj["scratchspace"] / "ty"
    scratchspace.mkdir(exist_ok=True)

    version = "0.0.1-alpha.17"
    logging.info(
        'Using hardcoded version {version} since ty has no "latest" releases out'
    )

    logging.info(f"Downloading ty {version} source code from github")
    dl_tgz(
        f"https://github.com/astral-sh/ty/archive/refs/tags/{version}.tar.gz",
        scratchspace,
    )
    extracted_dest = scratchspace / f"ty-{version}"
    logging.info(f"Wrote source code to {extracted_dest}")

    txts = ctx.obj["txts"]
    txt_dest = txts / f"ty-{version}.md"
    logging.info(f"Collecting ty md docs together and writing to {txt_dest}")
    collect("**.md", extracted_dest / "docs", txt_dest)

    logging.info(f"Done with ty {version}")


license_info["ty"] = "MIT License"
cli.add_command(ty)
