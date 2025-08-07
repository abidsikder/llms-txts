import logging

import click
import httpx
from bs4 import BeautifulSoup

from .cli import cli, collect, common_soup_clean, dl_tgz, gh_latest_tag
from .license_info import license_info


@click.command()
@click.pass_context
def ruff(ctx):
    scratchspace = ctx.obj["scratchspace"] / "ruff"
    scratchspace.mkdir(exist_ok=True)

    logging.info("Finding latest version of ruff")
    version = gh_latest_tag("astral-sh/ruff")

    logging.info(f"Downloading ruff {version} source code from github")
    download_url = (
        f"https://github.com/astral-sh/ruff/archive/refs/tags/{version}.tar.gz"
    )

    dl_tgz(download_url, scratchspace)
    extracted_dest = scratchspace / f"ruff-{version}"
    logging.info(f"Wrote source code to {extracted_dest}")

    txts = ctx.obj["txts"]
    txt_dest = txts / f"ruff-{version}.md"
    logging.info(f"Collecting ruff md docs together and writing to {txt_dest}")
    collect("**.md", extracted_dest / "docs", txt_dest)

    logging.info(f"Grabbing auto generated reference items from the docs website")
    text_maker = ctx.obj["text_maker"]
    for reference_url in [
        "https://docs.astral.sh/ruff/rules/",
        "https://docs.astral.sh/ruff/settings/",
    ]:
        resp = httpx.get(reference_url)
        soup = BeautifulSoup(resp.text, "lxml")
        soup = soup.select("article.md-content__inner.md-typeset")[0]

        common_soup_clean(soup)
        converted = text_maker.handle(str(soup))
        with txt_dest.open(mode="a") as f:
            f.write(converted)

    logging.info(f"Done with ruff {version}")


license_info["ruff"] = "MIT License"
cli.add_command(ruff)
