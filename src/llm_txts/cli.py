"""
Contains the click.group cli entrypoint, and any utility functions.
"""

import io
import itertools
import logging
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import click
import html2text
import httpx

from .license_info import license_info


def dl_zip(dl_url: str, dest: Path):
    """Download a zip file from a url and extract to a directory."""
    zip_resp = httpx.get(dl_url, follow_redirects=True)
    zip_buffer = io.BytesIO(zip_resp.content)
    with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
        zip_ref.extractall(dest)


def dl_tgz(url: str, dest: Path):
    """Download a .tar.gz file and write it to destination."""
    resp = httpx.get(url, follow_redirects=True)
    file = tarfile.open(fileobj=io.BytesIO(resp.content), mode="r|gz")
    file.extractall(path=dest)


def collect(pattern: str, source: Path, dest: Path, exclude=""):
    args = [
        "code2prompt",
        "--no-codeblock",
        "--no-clipboard",
        "--template",
        Path("code2prompt-minimal.hbs"),
        "--include",
        pattern,
        source,
        "--output-file",
        dest,
    ]
    # exclude patterns have to be nonempty or code2prompt ignores everything
    if len(exclude) > 0:
        args.append("--exclude")
        args.append(exclude)
    subprocess.run(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def gh_latest_tag(gh_id: str) -> str:
    """Give the github url without a forward slash at the end"""
    resp = httpx.get(f"https://github.com/{gh_id}/releases/latest")
    redirect_url = resp.headers["Location"]
    latest_tag = redirect_url.rsplit("/", 1)[-1]
    if latest_tag[0] == "v":
        latest_tag = latest_tag[1:]
    return latest_tag


def common_soup_clean(soup):
    # Remove intra-document links that just have a content of "#"
    for a_tag in soup.select('a[href^="#"]'):
        if a_tag.string == "#":
            a_tag.decompose()

    # Remove emphasis and italics
    for elem in soup.find_all("strong"):
        elem.unwrap()
    for elem in soup.find_all("em"):
        elem.unwrap()


@click.group()
@click.pass_context
def cli(ctx):
    if not Path("./.git").exists():
        logging.error(
            f"Must be called from the repo root! Being called from {Path.cwd()}"
        )
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",  # ISO 8601 format
        stream=sys.stderr,
    )

    ctx.ensure_object(dict)

    text_maker = html2text.HTML2Text()
    # options to shorten the text generated and use more of the context
    text_maker.ignore_images = True
    text_maker.body_width = 0  # no wrap for long lines of text
    text_maker.ignore_links = True
    text_maker.ignore_mailto_links = True
    text_maker.ignore_emphasis = True
    text_maker.ignore_tables = True
    text_maker.single_link_break = True
    ctx.obj["text_maker"] = text_maker

    # Create all working directories so that other commands don't have to worry about it.
    scratchspace = Path("scratchspace")
    site_build = Path("site-build")
    txts = site_build / "txts"

    scratchspace.mkdir(exist_ok=True)
    site_build.mkdir(exist_ok=True)
    txts.mkdir(exist_ok=True)

    ctx.obj["scratchspace"] = scratchspace
    ctx.obj["site-build"] = site_build
    ctx.obj["txts"] = txts


@click.command
@click.pass_context
def build_site(ctx):
    logging.info("Constructing index.html with the list of all files")
    index_html = io.StringIO()
    head = """<!doctype html><html>
    <head><title>llm-txts</title></head>
    <body>
    <h1>llm-txts for use with your favorite long context LLM or RAG system.</h1>

    <a href="https://github.com/abidsikder/llm-txts" target="_blank">GitHub</a>
    <ul>
    """
    index_html.write(head)

    txts = ctx.obj["txts"]
    txt_ps = list(itertools.chain(txts.rglob("*.txt"), txts.rglob("*.md")))
    # go through things alphabetically so that the website has a list in an alphabetical format
    txt_ps = sorted(txt_ps)
    for txt_p in txt_ps:
        size_bytes = txt_p.stat().st_size
        approx_tokens = (
            size_bytes / 4
        )  # rough approximation by dividing by 4 characters per token
        rounded = round(approx_tokens / 1000)
        # e.g. <li><a href="txts/python-3.13.5.txt" download>python-3.13.5.txt</a> ~ 2856K tokens</li>
        tag = f'<li><a href="txts/{txt_p.name}" download>{txt_p.name}</a> ~ {rounded}K tokens</li>'
        index_html.write(tag)

    middle = """
    </ul>
    <h3>License Acknowledgments</h3>
    <ul>
    """
    index_html.write(middle)

    tool_names = sorted(list(license_info.keys()))
    for tool_name in tool_names:
        license = license_info[tool_name]
        index_html.write(
            f"<li>{tool_name} documentation is licensed under {license}</li>"
        )

    foot = """
    </ul>
    </body>
    </html>
    """
    index_html.write(foot)

    site_build = ctx.obj["site-build"]
    (site_build / "index.html").write_text(index_html.getvalue())
    logging.info("Done with building website")


cli.add_command(build_site)
