import logging
import subprocess

import click
from bs4 import BeautifulSoup

from .cli import cli, collect, common_soup_clean, dl_tgz, gh_latest_tag
from .license_info import license_info

license_info["xarray"] = "Apache License 2.0"


@click.command
@click.pass_context
@click.option("--version")
def xarray(ctx, version: str | None):
    scratchspace = ctx.obj["scratchspace"] / "xarray"
    scratchspace.mkdir(exist_ok=True)

    if version is None:
        logging.info("Finding latest version of xarray since none was specified")
        version = gh_latest_tag("pydata/xarray")

    logging.info(f"Downloading xarray {version} source from github")
    dl_tgz(
        f"https://github.com/pydata/xarray/archive/refs/tags/v{version}.tar.gz",
        scratchspace,
    )
    extracted = scratchspace / f"xarray-{version}"

    txt_dest = ctx.obj["txts"] / f"xarray-{version}.txt"
    logging.info(f"Collating rst files into initial txt at {txt_dest}")
    collect(
        "user-guide/**.rst,getting-started-guide/**.rst,get-help/**.rst",
        extracted / "doc",
        txt_dest,
    )

    logging.info(
        "Grabbing xarray's detailed api documentation and adding it to the txt"
    )
    curl_resp = subprocess.run(
        ["curl", "-L", f"https://docs.xarray.dev/en/v{version}/api.html"],
        check=True,
        capture_output=True,
    )
    soup = BeautifulSoup(curl_resp.stdout.decode(), "lxml")
    soup = BeautifulSoup(
        str(list(soup.find_all("article", class_="bd-article"))[0]), "lxml"
    )
    common_soup_clean(soup)
    text_maker = ctx.obj["text_maker"]
    converted = text_maker.handle(str(soup))
    with txt_dest.open(mode="a") as f:
        f.write(converted)

    logging.info(f"Done processing xarray {version}")


cli.add_command(xarray)
