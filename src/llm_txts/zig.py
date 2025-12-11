import logging
import re

import click
import httpx
from bs4 import BeautifulSoup

from .cli import cli, common_soup_clean
from .license_info import license_info

license_info["zig"] = "MIT License"


@click.group
@click.pass_context
def zig(ctx):
    scratchspace = ctx.obj["scratchspace"] / "zig"
    scratchspace.mkdir(exist_ok=True)


@click.command(name="lang_ref")
@click.pass_context
@click.argument("version", type=str)
def zig_lang_ref(ctx, version: str):
    """
    Compile language reference. Only caches non-master branch versions on local disk
    """
    scratchspace = ctx.obj["scratchspace"] / "zig"
    webpage_cache_name = f"zig_language_reference-{version}.html"
    webpage_cached = scratchspace / webpage_cache_name
    if not webpage_cached.exists() or version == "master":
        webpage_html = httpx.get(
            f"https://ziglang.org/documentation/{version}/", follow_redirects=True
        ).text
        webpage_cached.write_text(webpage_html)
    else:
        webpage_html = webpage_cached.read_text()
    soup = BeautifulSoup(webpage_html, "lxml")

    for elem in soup.find_all("div", id="navigation"):
        elem.decompose()
    common_soup_clean(soup)
    cleaned_html = str(soup)

    text_maker = ctx.obj["text_maker"]
    converted = text_maker.handle(cleaned_html)
    if version == "master":
        pattern = r'zig_version_string = "([^"]*)"'
        match = re.search(pattern, converted)
        version = match.group(1)

    txts = ctx.obj["txts"]
    txt_dest = txts / f"zig-language-ref-{version}.md"
    txt_dest.write_text(converted)

    logging.info(f"Done with zig language reference {version}")


zig.add_command(zig_lang_ref)
cli.add_command(zig)
