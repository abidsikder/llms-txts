import logging

import click
import httpx

from .cli import cli
from .license_info import license_info

license_info["typst"] = "Apache 2.0 License"


@click.command()
@click.pass_context
def typst(ctx):
    logging.info(
        f"Downloading typst 0.13.1 docs.md from github.com/abidsikder/typst-docs/single-file"
    )
    download_url = "https://raw.githubusercontent.com/abidsikder/typst-docs-single-file/refs/heads/main/docs.md"
    resp = httpx.get(download_url, follow_redirects=True)

    txt_dest = ctx.obj["txts"] / "typst.md"
    with txt_dest.open("w") as f:
        f.write(resp.text)

    logging.info(f"Done with typst")


cli.add_command(typst)
