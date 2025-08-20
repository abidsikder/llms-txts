import logging
import shutil

import click

from .cli import cli, dl_zip
from .license_info import license_info

license_info["boto3"] = "3-clause BSD license"


@click.command
@click.pass_context
def networkx(ctx):
    scratchspace = ctx.obj["scratchspace"] / "networkx"
    scratchspace.mkdir(exist_ok=True)

    version = "3.5"
    logging.info(
        f"Downloading networkx {version} llms.txt from github.com/abidsikder/networkx-llms-txt"  # noqa: E501
    )
    dl_zip(
        "https://github.com/abidsikder/networkx-llms-txt/archive/refs/heads/llmsmd.zip",
        scratchspace,
    )
    extracted = scratchspace / "networkx-llms-txt-llmsmd"
    source = extracted / "doc" / f"networkx-{version}.md"
    dest = ctx.obj["txts"] / source.name
    shutil.copyfile(source, dest)

    logging.info("Done copying over networkx llms.txt")


cli.add_command(networkx)
