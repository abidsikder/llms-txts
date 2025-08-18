import logging

import click

from .cli import cli, collect, dl_zip
from .license_info import license_info


@click.command()
@click.pass_context
def hy(ctx):
    scratchspace = ctx.obj["scratchspace"] / "hy"
    scratchspace.mkdir(exist_ok=True)

    version = "1.1.0"
    logging.info(
        f"Downloading hy {version} txts from github.com/abidsikder/hy-llms-txt"
    )
    dl_zip(
        "https://github.com/abidsikder/hy-llms-txt/archive/refs/heads/master.zip",
        scratchspace,
    )
    extracted = scratchspace / "hy-llms-txt-master"

    txts = ctx.obj["txts"]
    txt_dest = txts / f"hy-{version}.txt"
    collect(
        "*.txt", extracted / "docs-txts", txt_dest, exclude="index.txt,versioning.txt"
    )

    logging.info("Done with hy")


license_info["hy"] = """
<a href="https://github.com/hylang/hy?tab=License-1-ov-file" target="_blank">
hy license
</a>
"""
cli.add_command(hy)
