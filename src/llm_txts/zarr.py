import logging

import click

from .cli import cli, collect, dl_zip, gh_latest_tag
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

    logging.info(f"Downloading html zip of zarr {version} from readthedocs")
    extracted = dl_ex_zip(
        f"https://zarr.readthedocs.io/_/downloads/en/v{version}/htmlzip/",
        scratchspace / version / f"zarr-v{version}.zip",
    )
    logging.info("Converting the html documentation to text")
    index_html_p = extracted / "index.html"
    index_html = index_html_p.read_text()
    text_maker = ctx.obj["text_maker"]
    converted = text_maker.handle(index_html)
    final_txt_p = ctx.obj["txts"] / f"zarr-{version}.txt"
    logging.info(f"Writing collated txt to {final_txt_p}")
    final_txt_p.write_text(converted)
    logging.info(f"Done with zarr {version}")


cli.add_command(zarr)
