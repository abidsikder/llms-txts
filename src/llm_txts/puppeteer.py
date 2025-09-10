import logging

import click

from .cli import cli, collect, dl_zip
from .license_info import license_info

license_info["puppeteer"] = "Apache 2.0 License"


@click.command
@click.pass_context
@click.option("--version", default="24.19.0", help="puppeteer version specifier")
def puppeteer(ctx, version: str):
    scratchspace = ctx.obj["scratchspace"] / "puppeteer"
    scratchspace.mkdir(exist_ok=True)

    logging.info(
        f"Downloading puppeteer {version} md docs from github.com/puppeteer/puppeteer"
    )
    dl_zip(
        f"https://github.com/puppeteer/puppeteer/archive/refs/tags/puppeteer-v{version}.zip",
        scratchspace,
    )
    extracted = scratchspace / f"puppeteer-puppeteer-v{version}"

    txt_dest = ctx.obj["txts"] / f"puppeteer-v{version}.md"
    collect(
        "docs/**.md",
        extracted,
        txt_dest,
    )

    logging.info("Done collecting puppeteer markdown docs")


cli.add_command(puppeteer)
