import io
import logging
import tempfile
from pathlib import Path

import click
from bs4 import BeautifulSoup

from .cli import cli, collect, common_soup_clean, dl_tgz, gh_latest_tag
from .license_info import license_info

license_info["mlx"] = "MIT License"


@click.command
@click.pass_context
def mlx(ctx):
    scratchspace = ctx.obj["scratchspace"] / "mlx"
    scratchspace.mkdir(exist_ok=True)

    logging.info("Getting mlx version")
    version = gh_latest_tag("ml-explore/mlx")

    # This is done since correlating between the gh-pages and the github tag commits is very difficult
    logging.info("Downloading the latest version's gh-pages build")
    dl_tgz(
        "https://github.com/ml-explore/mlx/archive/refs/heads/gh-pages.tar.gz",
        scratchspace,
    )
    with tempfile.NamedTemporaryFile(mode="w+", delete=True, suffix=".html") as fp:
        logging.info("Processing built html into the final markdown")
        collected_html_p = Path(fp.name)
        collect(
            "dev/**.html,examples/**.html,python/**.html",
            scratchspace / "mlx-gh-pages" / "docs" / "build" / "html",
            collected_html_p,
        )
        soup = BeautifulSoup(collected_html_p.read_text(), "lxml")
        filtered = io.StringIO()
        for elem in soup.find_all("article", class_="bd-article"):
            filtered.write(str(elem))
        soup = BeautifulSoup(filtered.getvalue(), "lxml")

        common_soup_clean(soup)

        text_maker = ctx.obj["text_maker"]
        converted = text_maker.handle(str(soup))

        txt_dest = ctx.obj["txts"] / f"mlx-{version}.md"
        with txt_dest.open(mode="w") as f:
            f.write(converted)

    logging.info(f"Done processing mlx {version}")


cli.add_command(mlx)
