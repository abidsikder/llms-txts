import logging

import click
import httpx
from bs4 import BeautifulSoup

from .cli import cli
from .license_info import license_info

license_info["Node.js"] = """
<a href="https://github.com/nodejs/node?tab=License-1-ov-file" target="_blank">
Node.js license
</a>
"""


@click.command
@click.pass_context
@click.argument("version", type=str)
def nodejs(ctx, version: str):
    """
    Version is the major version, e.g. 22, 23, 24.
    """
    scratchspace = ctx.obj["scratchspace"] / "nodejs"
    scratchspace.mkdir(exist_ok=True)

    logging.info("Downloading documentation page for parsing")
    download_url = f"https://nodejs.org/docs/latest-v{version}.x/api/all.html"
    resp = httpx.get(download_url)

    soup = BeautifulSoup(resp.text, "lxml")
    content_div = soup.find("div", id="apicontent")
    for copy_button in content_div.find_all("button", class_="copy-button"):
        copy_button.decompose()
    for code_block in content_div.find_all("code", class_="language-js cjs"):
        code_block.decompose()

    text_maker = ctx.obj["text_maker"]
    converted = text_maker.handle(str(content_div))

    txt_dest = ctx.obj["txts"] / f"nodejs-{version}.md"
    txt_dest.write_text(converted)

    logging.info(f"Done processing Node.js major version {version}")


cli.add_command(nodejs)
