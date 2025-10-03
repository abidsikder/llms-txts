import logging

import click

from .cli import cli, collect, dl_tgz, dl_zip_curl, gh_latest_tag
from .license_info import license_info

license_info["zarr"] = "MIT License"


@click.command
@click.pass_context
@click.option("--version")
def zarr(ctx, version: str | None):
    scratchspace = ctx.obj["scratchspace"] / "zarr"
    scratchspace.mkdir(exist_ok=True)

    if version is None:
        logging.info("Finding latest version of zarr since none was specified")
        version = gh_latest_tag("zarr-developers/zarr-python")

    logging.info(f"Downloading zarr {version} source from github")
    dl_tgz(
        f"https://github.com/zarr-developers/zarr/archive/refs/tags/v{version}.tar.gz",
        scratchspace,
    )
    extracted = scratchspace / f"zarr-python-{version}"
    txt_dest = ctx.obj["txts"] / f"zarr-{version}.md"
    logging.info(f"Collating user guide files into initial txt at {txt_dest}")
    txt_dest.write_text("a")
    collect(
        "**.rst",
        extracted / "docs" / "user-guide",
        txt_dest,
    )

    logging.info(f"Downloading and adding zarr {version} detailed api documentation")
    dl_zip_curl(
        f"https://zarr.readthedocs.io/_/downloads/en/v{version}/htmlzip/",
        scratchspace / f"zarr-v{version}.zip",
    )
    extracted = scratchspace / f"zarr-v{version}"
    index_html_p = extracted / "index.html"
    index_html = index_html_p.read_text()
    text_maker = ctx.obj["text_maker"]
    converted = text_maker.handle(index_html)
    with txt_dest.open("a") as f:
        f.write(converted)
    logging.info(f"Done with zarr {version}")


cli.add_command(zarr)
