import logging
import shutil

import click

from .cli import cli, dl_zip
from .license_info import license_info

license_info["boto3"] = "Apache 2.0 License"


@click.command
@click.pass_context
def boto3(ctx):
    scratchspace = ctx.obj["scratchspace"] / "boto3"
    scratchspace.mkdir(exist_ok=True)

    version = "1.40.6"
    logging.info(
        f"Downloading boto3 {version} txts from github.com/abidsikder/boto3-llms-txt"
    )
    dl_zip(
        "https://github.com/abidsikder/boto3-llms-txt/archive/refs/heads/master.zip",
        scratchspace,
    )
    extracted = scratchspace / "boto3-llms-txt-master"
    for boto3_txt in (extracted / "docs" / "txts").glob("*.txt"):
        txt_dest = ctx.obj["txts"] / f"boto3-{version}-{boto3_txt.name}"
        shutil.copyfile(boto3_txt, txt_dest)

    logging.info("Done copying over all boto3 txts")


cli.add_command(boto3)
