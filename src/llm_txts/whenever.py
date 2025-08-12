import logging
import threading

import click
import httpx
from bs4 import BeautifulSoup

from .cli import cli, gh_latest_tag
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

    # This is done since correlating between the gh-pages and the github tag commits is very difficult
    logging.info("Downloading the latest version html pages from readthedocs")
    texts: list[str] = []
    text_maker = ctx.obj["text_maker"]

    def process_page(url: str):
        html = httpx.get(url).text
        soup = BeautifulSoup(html, "lxml")
        main_content = list(soup.find_all("article", id="furo-main-content"))[0]
        text = text_maker.handle(str(main_content))
        texts.append(text)

    docs_urls = [
        "https://whenever.readthedocs.io/en/latest/index.html",
        "https://whenever.readthedocs.io/en/latest/examples.html",
        "https://whenever.readthedocs.io/en/latest/overview.html",
        "https://whenever.readthedocs.io/en/latest/deltas.html",
        "https://whenever.readthedocs.io/en/latest/faq.html",
        "https://whenever.readthedocs.io/en/latest/api.html#",
    ]

    threads = [threading.Thread(target=process_page, args=(url,)) for url in docs_urls]
    threads.append(threading.Thread(target=get_version))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    txt_dest = ctx.obj["txts"] / f"whenever-{version}.md"
    with txt_dest.open(mode="w") as f:
        for text in texts:
            f.write(text)

    logging.info(f"Done processing whenever {version}")


cli.add_command(whenever)
