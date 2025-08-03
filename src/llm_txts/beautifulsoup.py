import logging

import click
import httpx

from .cli import cli


@click.command
@click.pass_context
def beautifulsoup(ctx):
    txt_dest = ctx.obj["txts"] / "beautifulsoup-vNA.txt"
    logging.info("Downloading documentation website rst source to txt")
    resp = httpx.get(
        "https://www.crummy.com/software/BeautifulSoup/bs4/doc/_sources/index.rst.txt"
    )
    with txt_dest.open(mode="a") as f:
        f.write(resp.text)
    logging.info("Done with beautifulsoup")


cli.add_command(beautifulsoup)
