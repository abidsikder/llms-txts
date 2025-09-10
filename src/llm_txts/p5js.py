import io
import json
import logging

import click
import httpx

from .cli import cli
from .license_info import license_info

license_info["p5.js"] = "LGPL-2.1 License"


@click.command
@click.pass_context
def p5js(ctx):
    scratchspace = ctx.obj["scratchspace"] / "p5js"
    scratchspace.mkdir(exist_ok=True)

    logging.info("Downloading p5js docs data")
    resp = httpx.get("https://p5js.org/reference/data.json")
    docs_data = json.loads(resp.text)
    version = docs_data["project"]["version"]

    logging.info(f"Got version {version}")
    txt = io.StringIO()
    text_maker = ctx.obj["text_maker"]

    def write(s):
        txt.write(s)
        txt.write("\n")

    ignored_properties = ["file", "line", "fors", "requires", "final"]

    def recurse(d, depth):
        for key, value in d.items():
            if key in ignored_properties or value == 1:
                continue
            elif isinstance(value, list):
                recurse(dict(enumerate(value)), depth + 1)
            elif isinstance(value, dict):
                if isinstance(key, str):  # ignore int list enumerated dict keys
                    write(("#" * depth) + " " + key)
                recurse(value, depth + 1)
            elif isinstance(value, str):
                value = value.replace("\\n", "\n")
                write(text_maker.handle(value))
            else:
                write(text_maker.handle(str(value)))

    recurse(docs_data, 1)

    txt_dest = ctx.obj["txts"] / f"p5js-{version}.md"
    txt_dest.write_text(txt.getvalue())

    logging.info(f"Done collecting p5.js {version} docs")


cli.add_command(p5js)
