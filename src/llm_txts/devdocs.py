"""
For all documentation sets derived from devdocs.io
"""

import json
import logging
import shutil
import tempfile
from pathlib import Path

import click
import httpx
from bs4 import BeautifulSoup

from .cli import cli, collect, common_soup_clean, dl_tgz
from .license_info import license_info


def dl_devdocs(slug: str, dest: Path):
    """Download and extract a .tar.gz file from devdocs"""
    dl_tgz(f"https://downloads.devdocs.io/{slug}.tar.gz", dest)


def devdocs(tool_name: str):
    @click.command(name=tool_name)
    @click.option("--version", help="Has to match the version available on devdocs.io.")
    @click.pass_context
    def f(ctx, version: str | None):
        scratchspace = ctx.obj["scratchspace"] / tool_name
        scratchspace.mkdir(exist_ok=True)

        slug = tool_name
        if version is not None:
            slug = slug + "~" + version
        # If it's numpy and a version was not specified, we need to find it, we can't just say numpy for the slug
        elif tool_name == "numpy":
            logging.info(
                f"Need to find latest version for {tool_name}, finding list of all available versions"
            )
            list_of_all_docs = json.load(httpx.get("https://devdocs.io/docs/docs.json"))
            versions = []
            for d in list_of_all_docs:
                if tool_name in d["slug"]:
                    versions.append(d["version"])
            latest_version = sorted(versions)[-1]
            slug = slug + "~" + latest_version

        logging.info(f"Downloading {slug} docs from devdocs")
        version: str = "vNA"
        download_dir = scratchspace / version
        dl_devdocs(slug, download_dir)

        meta_info = json.loads((download_dir / "meta.json").read_text())
        if "release" in meta_info:
            version = meta_info["release"]
            renamed = download_dir.with_stem(version)
            if renamed.exists():
                shutil.rmtree(renamed)
            download_dir.replace(renamed)
            download_dir = renamed

        logging.info(f"Downloaded {tool_name} {version} docs into {download_dir}")

        logging.info(f"Cleaning up html and parsing it into a collated txt")
        txt_dest = ctx.obj["txts"] / f"{tool_name}-{version}.md"
        with tempfile.NamedTemporaryFile(mode="w+", delete=True, suffix=".html") as fp:
            collected_html_p = Path(fp.name)
            match tool_name:
                case "numpy":
                    collect(
                        "user/**.html,reference/**.html",
                        download_dir,
                        collected_html_p,
                        exclude="reference/c-api/**.html,reference/distutils/**.html,reference/distutils*.html",
                    )
                case "javascript":
                    collect(
                        "**.html",
                        download_dir,
                        collected_html_p,
                        exclude="global_objects/**.html",
                    )
                    with tempfile.NamedTemporaryFile(
                        mode="w+", delete=True, suffix=".html"
                    ) as fp2:
                        collected_html_p2 = Path(fp2.name)
                        collect(
                            "global_objects/*.html",
                            download_dir,
                            collected_html_p2,
                        )
                        fp.write(collected_html_p2.read_text())
                case _:
                    collect("**.html", download_dir, collected_html_p)

            soup = BeautifulSoup(collected_html_p.read_text(), "lxml")

            # Clean up the context by removing unnecessary information
            for elem in soup.find_all("div", class_="_attribution"):
                elem.decompose()
            # Clean up browser compatibility information from dom/html/css to reduce total size
            match tool_name:
                case "dom" | "html" | "css" | "javascript":
                    for elem in soup.find_all("details", class_="baseline-indicator"):
                        elem.decompose()
                    for elem in soup.select("h2#specifications + div._table"):
                        elem.decompose()
                    for elem in soup.find_all(
                        "h2", id="specifications"
                    ):  # the above doesn't destroy the h2 itself for some reason...
                        elem.decompose()
                    for elem in soup.select("h2#browser_compatibility + div._table"):
                        elem.decompose()
                    for elem in soup.find_all("h2", id="browser_compatibility"):
                        elem.decompose()

            common_soup_clean(soup)

            text_maker = ctx.obj["text_maker"]
            converted = text_maker.handle(str(soup))
            with txt_dest.open(mode="w") as f:
                f.write(converted)

        logging.info(f"Done processing {tool_name} {version}")

    return f


license_info["dom / Web APIs"] = (
    "Creative Commons Attribution-ShareAlike License v2.5 or later"
)
cli.add_command(devdocs("dom"))

license_info["css"] = "Creative Commons Attribution-ShareAlike License v2.5 or later"
cli.add_command(devdocs("css"))

license_info["html"] = "Creative Commons Attribution-ShareAlike License v2.5 or later"
cli.add_command(devdocs("html"))

license_info["javascript"] = (
    "Creative Commons Attribution-ShareAlike License v2.5 or later"
)
cli.add_command(devdocs("javascript"))

license_info["typescript"] = "Apache License, Version 2.0"
cli.add_command(devdocs("typescript"))

license_info["svelte"] = "MIT License"
cli.add_command(devdocs("svelte"))

license_info["vite"] = "MIT License"
cli.add_command(devdocs("vite"))

license_info["vitest"] = "MIT License"
cli.add_command(devdocs("vitest"))

license_info["git"] = "GPLv2"
cli.add_command(devdocs("git"))

license_info["bash"] = "GNU Free Documentation License"
cli.add_command(devdocs("bash"))

license_info["zsh"] = "MIT License"
cli.add_command(devdocs("zsh"))

license_info["homebrew"] = "BSD 2-Clause License"
cli.add_command(devdocs("homebrew"))

license_info["jq"] = "Creative Commons Attribution 3.0 license"
cli.add_command(devdocs("jq"))

license_info["numpy"] = "3-clause BSD License"
cli.add_command(devdocs("numpy"))

license_info["pytorch"] = (
    "the pytorch BSD-like license https://github.com/pytorch/pytorch/blob/main/LICENSE"
)
cli.add_command(devdocs("pytorch"))

license_info["click"] = "BSD 3-Clause License"
cli.add_command(devdocs("click"))
