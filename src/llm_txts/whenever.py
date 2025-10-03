import logging
import threading

import click
from bs4 import BeautifulSoup

from .cli import cli, dl_zip_curl, gh_latest_tag
from .license_info import license_info

license_info["whenever"] = "MIT License"


@click.command
@click.pass_context
def whenever(ctx):
    scratchspace = ctx.obj["scratchspace"] / "whenever"
    scratchspace.mkdir(exist_ok=True)

    version = None

    def get_version():
        nonlocal version
        logging.info("Determining the latest version specifier")
        version = gh_latest_tag("ariebovenberg/whenever")

    converted: str = ""

    def process_downloaded_html():
        logging.info("Downloading the latest version html pages from readthedocs")
        # Use curl because httpx seems to be blocked by readthedocs
        dl_zip_curl(
            "https://whenever.readthedocs.io/_/downloads/en/latest/htmlzip/",
            scratchspace / "whenever-latest.zip",
        )
        extracted = scratchspace / "whenever-latest"
        logging.info("Converting the downloaded html to markdown")
        soup = BeautifulSoup((extracted / "index.html").read_text(), "lxml")
        main_content = list(soup.find_all("article", id="furo-main-content"))[0]
        for elem in main_content.find_all("section", id="changelog"):
            elem.decompose()
        text_maker = ctx.obj["text_maker"]
        nonlocal converted
        converted = text_maker.handle(str(main_content))

    version_thread = threading.Thread(target=get_version)
    html_thread = threading.Thread(target=process_downloaded_html)

    version_thread.start()
    html_thread.start()

    version_thread.join()
    html_thread.join()

    txt_dest = ctx.obj["txts"] / f"whenever-{version}.md"
    with txt_dest.open(mode="w") as f:
        f.write(converted)

    logging.info(f"Done processing whenever {version}")


cli.add_command(whenever)
