import logging

import click
import httpx
from bs4 import BeautifulSoup

from .cli import cli, collect, common_soup_clean, dl_tgz, gh_latest_tag
from .license_info import license_info

license_info["icechunk"] = "Apache License 2.0"


@click.command
@click.pass_context
@click.option("--version")
def icechunk(ctx, version: str | None):
    scratchspace = ctx.obj["scratchspace"] / "icechunk"
    scratchspace.mkdir(exist_ok=True)

    if version is None:
        logging.info("Finding latest version of icechunk since none was specified")
        version = gh_latest_tag("earth-mover/icechunk")

    # Get most of the docs from the handwritten markdown tutorials in the code repository
    logging.info(f"Downloading icechunk {version} source code")
    download_url = (
        f"https://github.com/earth-mover/icechunk/archive/refs/tags/v{version}.tar.gz"
    )
    dl_tgz(download_url, scratchspace)
    extracted = scratchspace / f"icechunk-{version}"
    logging.info("Collecting handwritten docs from source code")
    txt_dest = ctx.obj["txts"] / f"icechunk-{version}.txt"
    collect("**.md", extracted / "docs" / "docs", txt_dest)

    logging.info("Collecting the auto generated api docs from the website")
    resp = httpx.get(f"https://icechunk.io/en/v{version}/reference/")
    soup = BeautifulSoup(resp.text, "lxml")
    content_div = soup.find("div", class_="md-content")
    # these are pieces of the source code along with line numbers below each line of the api documentation, they are unnecessary and clutter up the context with a bunch of line numbers
    for elem in content_div.find_all("details", class_="quote"):
        elem.decompose()
    common_soup_clean(content_div)

    text_maker = ctx.obj["text_maker"]
    converted = text_maker.handle(str(content_div))

    with txt_dest.open(mode="a") as f:
        f.write(converted)

    logging.info(f"Done processing icechunk {version}")


cli.add_command(icechunk)
