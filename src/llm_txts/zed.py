import logging

import click

from .cli import cli, collect, dl_tgz, gh_latest_tag
from .license_info import license_info

license_info["zed"] = "GNU AGPLv3"


@click.command
@click.pass_context
@click.option("--version")
def zed(ctx, version: str | None):
    scratchspace = ctx.obj["scratchspace"] / "zed"
    scratchspace.mkdir(exist_ok=True)

    if version is None:
        logging.info("Finding latest version of zed since none was specified")
        version = gh_latest_tag("zed-industries/zed")

    logging.info(f"Downloading zed {version} source code from github")
    download_url = (
        f"https://github.com/zed-industries/zed/archive/refs/tags/v{version}.tar.gz"
    )
    dl_tgz(download_url, scratchspace)
    extracted_dest = scratchspace / f"zed-{version}"
    logging.info(f"Wrote source code to {extracted_dest}")

    txts = ctx.obj["txts"]
    txt_dest = txts / f"zed-{version}.md"
    logging.info(f"Collecting zed md docs together and writing to {txt_dest}")
    collect("**.md", extracted_dest, txt_dest)

    logging.info(f"Done with zed {version}")


cli.add_command(zed)
