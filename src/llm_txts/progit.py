import logging

import click

from .cli import cli, collect, dl_tgz
from .license_info import license_info

license_info["progit book"] = (
    "Creative Commons Attribution Non Commercial Share Alike 3.0"
)


@click.command
@click.pass_context
def progit(ctx):
    scratchspace = ctx.obj["scratchspace"] / "progit"
    scratchspace.mkdir(exist_ok=True)

    logging.info("Downloading progit2 contents from github")
    dl_tgz(
        "https://github.com/progit/progit2/archive/refs/heads/main.tar.gz", scratchspace
    )
    txt_dest = ctx.obj["txts"] / "git-progit2.txt"
    logging.info(f"Collecting writing together to {txt_dest}")
    collect("**.asc", scratchspace, txt_dest)
    logging.info("Done with progit")


cli.add_command(progit)
