import io
import re
import shutil
import subprocess
import sys
import typing
import zipfile
from pathlib import Path

import click
import html2text
import httpx
from bs4 import BeautifulSoup


def ep(s):
    print(s, file=sys.stderr)


def dl_ex_zip(dl_url: str, dest: Path) -> Path:
    """Download a zip file from a url and put it at a destination. Then extract the contents and place it inside that same directory. Return the directory containing the unzipped files.

    You should name the zarr destination path as the same name as what the directory will look like after it comes out of the zip, so that the extracted name works.
    """
    while True:
        zip_resp = httpx.get(dl_url)
        if zip_resp.status_code != 302:
            break
        dl_url = zip_resp.headers["Location"]

    dest.parent.mkdir(exist_ok=True, parents=True)
    with open(dest, "wb") as f:
        f.write(zip_resp.content)

    extracted: Path
    with zipfile.ZipFile(dest, "r") as zip_ref:
        zip_ref.extractall(dest.parent)
        extracted = Path(zip_ref.filename).with_suffix("")

    return extracted


def collect(pattern: str, source: Path, dest: Path):
    subprocess.run(
        [
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
        ],
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


@click.group()
def cli():
    if not Path("./.git").exists():
        ep(f"Must be called from the repo root! Being called from {Path.cwd()}")
        sys.exit(1)

    # Create all working directories so that other commands don't have to worry about it.
    Path("scratchspace").mkdir(exist_ok=True)
    Path("site-build").mkdir(exist_ok=True)
    Path("txts").mkdir(exist_ok=True)


@click.command
@click.argument("minor-version", type=str)
def python(minor_version: str):
    Path("scratchspace/python").mkdir(exist_ok=True)

    ep("Finding the latest patch version")
    response = httpx.get("https://www.python.org/ftp/python/")
    soup = BeautifulSoup(response.text, "html.parser")
    version_pattern = re.compile(r"^" + re.escape(minor_version) + r"\.(\d+)/$")
    patch_versions = []
    # Find all anchor tags (links)
    for link in soup.find_all("a"):
        href = link.get("href")
        match = version_pattern.match(href)
        if match:
            # Extract the patch number (the first group in the regex)
            patch_num = int(match.group(1))
            patch_versions.append(patch_num)
    latest_patch = max(patch_versions)
    latest_version = f"{minor_version}.{latest_patch}"
    ep(f"Found version {latest_version}")

    version_p = Path(f"scratchspace/python/{latest_version}")
    version_p.mkdir(exist_ok=True)

    download_url = f"https://www.python.org/ftp/python/doc/{latest_version}/python-{latest_version}-docs-text.zip"
    zip_dest = version_p / f"python-{latest_version}-docs-text.zip"
    ep("Downloading documentation txt zip and extracting")
    docs_dest = dl_ex_zip(download_url, zip_dest)
    final_txt_path = Path(f"txts/python-{latest_version}.txt")
    ep(
        f"Collecting all doc txts into a single txt and placing it inside of {final_txt_path}"
    )
    collect("*.txt", docs_dest, final_txt_path)
    ep(f"Done processing python version {latest_version}")


cli.add_command(python)


@click.command
@click.option("--version")
def zed(version: str | None):
    Path("scratchspace/zed").mkdir(exist_ok=True)

    latest_version: str = version
    if latest_version is None:
        latest_version = gh_latest_tag("zed-industries/zed")

    ep(f"Downloading version {latest_version} source code zip from github")
    download_url = (
        f"https://github.com/zed-industries/zed/archive/refs/tags/v{latest_version}.zip"
    )
    zip_dest = Path(f"scratchspace/zed/zed-{latest_version}.zip")
    extracted = dl_ex_zip(download_url, zip_dest)

    ep(f"Collecting zed md docs together and placing it into txts/")
    collect("*.md", extracted / "docs" / "src", Path(f"txts/zed-{latest_version}.txt"))

    ep(f"Done with Zed {latest_version}")


cli.add_command(zed)


def astral_sh(tool_name: typing.Literal["ruff", "uv"]):
    @click.command(name=tool_name)
    @click.option("--version")
    def f(version: str | None):
        Path(f"scratchspace/{tool_name}").mkdir(exist_ok=True)

        latest_version: str = version
        if version is None:
            latest_version = gh_latest_tag(f"astral-sh/{tool_name}")

        ep(f"Downloading version {latest_version} source code zip from github")
        download_url = f"https://github.com/astral-sh/{tool_name}/archive/refs/tags/{latest_version}.zip"
        zip_dest = Path(f"scratchspace/{tool_name}/{tool_name}-{latest_version}.zip")
        extracted = dl_ex_zip(download_url, zip_dest)

        ep(f"Collecting {tool_name} md docs together and placing it into txts/")
        collect(
            "*.md", extracted / "docs", Path(f"txts/{tool_name}-{latest_version}.txt")
        )

        ep(f"Done with {tool_name} {latest_version}")

    return f


cli.add_command(astral_sh("ruff"))
cli.add_command(astral_sh("uv"))


@click.command
@click.option("--version")
def zarr(version: str | None):
    Path(f"scratchspace/zarr").mkdir(exist_ok=True)

    latest_version: str = version
    if version is None:
        latest_version = gh_latest_tag("zarr-developers/zarr-python")

    ep(f"Downloading html zip file of version {latest_version} from readthedocs")
    html_zip_dl_url = (
        f"https://zarr.readthedocs.io/_/downloads/en/v{latest_version}/htmlzip/"
    )
    extracted = dl_ex_zip(
        html_zip_dl_url,
        Path("scratchspace/zarr") / str(latest_version) / f"zarr-v{latest_version}.zip",
    )
    print(extracted)
    ep("Converting the html documentation to text...")
    index_html_p = extracted / "index.html"
    index_html = index_html_p.read_text()
    text_maker = html2text.HTML2Text()
    text_maker.ignore_images = True
    converted = text_maker.handle(index_html)
    final_txt_p = Path(f"txts/zarr-{latest_version}.txt")
    ep(f"Writing the output to {final_txt_p}")
    final_txt_p.write_text(converted)
    ep(f"Processing zarr {latest_version} done")


cli.add_command(zarr)


@click.command
@click.option("--version")
def icechunk(version: str | None):
    Path(f"scratchspace/icechunk").mkdir(exist_ok=True)

    latest_version: str = version
    if version is None:
        latest_version = gh_latest_tag("earth-mover/icechunk")

    # Get most of the docs from the handwritten markdown tutorials in the code repository
    ep(f"Downloading source code of version {latest_version}")
    download_url = f"https://github.com/earth-mover/icechunk/archive/refs/tags/v{latest_version}.zip"
    zip_dest = Path(f"scratchspace/icechunk/icechunk-{latest_version}.zip")
    extracted = dl_ex_zip(download_url, zip_dest)
    ep(
        "Collecting handwritten docs from github repository, and auto generated api docs from website"
    )
    txt_dest = Path(f"txts/icechunk-{latest_version}.txt")
    collect("*.md", extracted / "docs" / "docs", txt_dest)

    # Grab the auto generated api documentation from the website
    resp = httpx.get(f"https://icechunk.io/en/v{latest_version}/reference/")
    # filter out non doc html stuff
    soup = BeautifulSoup(resp.text, "html.parser")
    content_div = soup.find("div", class_="md-content")
    # these are pieces of the source code along with line numbers below each line of the api documentation, they are unnecessary and clutter up the context with a bunch of line numbers
    quotes_to_remove = content_div.find_all("details", class_="quote")
    for quote in quotes_to_remove:
        quote.decompose()

    text_maker = html2text.HTML2Text()
    text_maker.ignore_images = True
    converted = text_maker.handle(str(content_div))

    # Add the converted text to the txt file that was already written
    with txt_dest.open(mode="a") as f:
        f.write(converted)

    ep(f"Done processing icechunk {latest_version}")


cli.add_command(icechunk)


@click.command
def build_site():
    ep("Constructing index.html with the list of all files...")
    index_html = io.StringIO()
    head = """
    <!doctype html>
    <html>
    <head>
    <title>llm-txts</title>
    </head>
    <body>
    <p>
    llm-txts for use with your favorite long context LLM or RAG system.
    </p>

    <a href="https://github.com/abidsikder/llm-txts" target="_blank">GitHub</a>
    <ul>
    """
    index_html.write(head)

    txt_ps = list(Path("txts/").rglob("*.txt"))
    txt_ps = sorted(
        txt_ps
    )  # go through things alphabetically so that the website has a list in an alphabetical format
    for txt_p in txt_ps:
        size_bytes = txt_p.stat().st_size
        approx_tokens = (
            size_bytes / 4
        )  # rough approximation by dividing by 4 characters per token
        rounded = round(approx_tokens / 1000)
        # looks like e.g. <li><a href="txts/python-3.13.5" download>python-3.13.5.txt</a> ~ 2856K tokens</li>
        tag = f'<li><a href="txts/{txt_p.name}" download>{txt_p.name}</a> ~ {rounded}K tokens</li>'
        index_html.write(tag)

    foot = """
    </ul>
    <h3>License Acknowledgments</h3>
    <ul>
    <li>pro git book is licensed under the Creative Commons Attribution Non Commercial Share Alike 3.0</li>
    <li>git documentation is licensed under the GPLv2</li>
    <li>zarr documentation is licensed under the MIT License</li>
    <li>icechunk documentation is licensed under the Apache License 2.0</li>
    <li>python3 documentation is licensed under the Python Software Foundation License Version 2</li>
    <li>zed editor documentation is licensed under GNU AGPLv3</li>
    <li>ruff, uv documentation is licensed under the MIT License</li>
    </ul>
    </body>
    </html>
    """
    index_html.write(foot)

    # Write out
    Path("site-build/index.html").write_text(index_html.getvalue())
    ep("Copying over all txts for website static assets...")
    shutil.copytree(Path("txts"), Path("site-build/txts"), dirs_exist_ok=True)
    ep("Done with building website")


cli.add_command(build_site)
