import logging
import re

import click
import httpx
from bs4 import BeautifulSoup

from .cli import cli, collect, dl_zip
from .license_info import license_info

license_info["python"] = "Python Software Foundation License Version 2"


@click.command
@click.pass_context
@click.argument("minor-version", type=str)
def python(ctx, minor_version: str):
    scratchspace = ctx.obj["scratchspace"] / "python"
    scratchspace.mkdir(exist_ok=True)

    logging.info(f"Finding the latest patch version for {minor_version}")
    response = httpx.get("https://www.python.org/ftp/python/")
    soup = BeautifulSoup(response.text, "lxml")
    version_pattern = re.compile(r"^" + re.escape(minor_version) + r"\.(\d+)/$")
    patch_versions = []
    # Find all anchor tags (links)
    for link in soup.find_all("a"):
        href = link.get("href")
        match = version_pattern.match(href)
        if match:
            # Extract the patch number (the first group in the regex)
            patch_num = int(match.group(1))
            patch_versions.append(patch_num)
    latest_patch = max(patch_versions)
    version = f"{minor_version}.{latest_patch}"
    logging.info(f"Found latest patch version {version}")

    logging.info("Downloading documentation txt zip and extracting")
    download_url = f"https://www.python.org/ftp/python/doc/{version}/python-{version}-docs-text.zip"
    dl_zip(download_url, scratchspace)
    txt_dest = ctx.obj["txts"] / f"python-{version}.txt"
    logging.info(
        f"Collecting all doc txts into a single txt and placing it inside of {txt_dest}"
    )
    collect(
        "library/**.txt",
        scratchspace / f"python-{version}-docs-text",
        txt_dest,
        exclude="stdtypes.txt,tk.txt,tkinter*.txt",
    )
    logging.info(f"Done processing python {version}")


cli.add_command(python)
