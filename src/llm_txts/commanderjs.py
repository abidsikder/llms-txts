import io
import logging
import threading

import click
import httpx
from bs4 import BeautifulSoup

from .cli import cli, dl_tgz
from .license_info import license_info

license_info["commander.js"] = "MIT License"


@click.command
@click.pass_context
def commanderjs(ctx):
    scratchspace = ctx.obj["scratchspace"] / "commanderjs"
    scratchspace.mkdir(exist_ok=True)

    version = "14.0.0"
    txt = io.StringIO()

    def source_docs():
        logging.info("Downloading source code docs for markdown help pages")
        download_url = (
            f"https://github.com/tj/commander.js/archive/refs/tags/v{version}.tar.gz"
        )
        dl_tgz(download_url, scratchspace)
        extracted = scratchspace / f"commander.js-{version}"
        for p in [
            extracted / "README.md",
            extracted / "docs" / "help-in-depth.md",
            extracted / "docs" / "options-in-depth.md",
            extracted / "docs" / "parsing-and-hooks.md",
            extracted / "docs" / "terminology.md",
        ]:
            txt.write(p.read_text())

    def jsdocs():
        logging.info("Downloading docs from jsdocs to get reference API build")
        resp = httpx.get("https://www.jsdocs.io/package/commander")
        soup = BeautifulSoup(resp.text, "lxml")
        text_maker = ctx.obj["text_maker"]
        for section_h2_id in [
            "variables",
            "functions",
            "classes",
            "interfaces",
            "type-aliases",
        ]:
            content_div = soup.find("h2", id=f"package-{section_h2_id}").find_parent(
                "section"
            )
            converted = text_maker.handle(str(content_div))
            txt.write(converted)

    source_docs_thread = threading.Thread(target=source_docs)
    jsdocs_thread = threading.Thread(target=jsdocs)

    source_docs_thread.start()
    jsdocs_thread.start()

    source_docs_thread.join()
    jsdocs_thread.join()

    txt_dest = ctx.obj["txts"] / f"commanderjs-{version}.md"
    txt_dest.write_text(txt.getvalue())

    logging.info(f"Done processing commanderjs {version}")


cli.add_command(commanderjs)
