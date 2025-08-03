import logging
import typing

import click

from .cli import cli, collect, dl_tgz, gh_latest_tag
from .license_info import license_info


def astral_sh(tool_name: typing.Literal["ruff", "uv"]):
    @click.command(name=tool_name)
    @click.pass_context
    @click.option("--version")
    def f(ctx, version: str | None):
        scratchspace = ctx.obj["scratchspace"] / tool_name
        scratchspace.mkdir(exist_ok=True)

        if version is None:
            logging.info(
                f"Finding latest version of {tool_name} since none was specified"
            )
            version = gh_latest_tag(f"astral-sh/{tool_name}")

        logging.info(f"Downloading {tool_name} {version} source code from github")
        download_url = f"https://github.com/astral-sh/{tool_name}/archive/refs/tags/{version}.tar.gz"

        dl_tgz(download_url, scratchspace)
        extracted_dest = scratchspace / f"{tool_name}-{version}"
        logging.info(f"Wrote source code to {extracted_dest}")

        txts = ctx.obj["txts"]
        txt_dest = txts / f"{tool_name}-{version}.txt"
        logging.info(
            f"Collecting {tool_name} md docs together and writing to {txt_dest}"
        )
        collect("**.md", extracted_dest, txt_dest)

        logging.info(f"Done with {tool_name} {version}")

    return f


license_info["ruff"] = "MIT License"
cli.add_command(astral_sh("ruff"))

license_info["uv"] = "MIT License"
cli.add_command(astral_sh("uv"))
