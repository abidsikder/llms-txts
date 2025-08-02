import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import typing
import zipfile
from pathlib import Path

import click
import html2text
import httpx
from bs4 import BeautifulSoup

license_info = dict()


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


def devdocs_dl(slug: str, dest: Path):
    """Download and extract a .tar.gz file from devdocs"""
    resp = httpx.get(f"https://downloads.devdocs.io/{slug}.tar.gz")
    file = tarfile.open(fileobj=io.BytesIO(resp.content), mode="r|gz")
    file.extractall(path=dest)


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


license_info["python"] = "Python Software Foundation License Version 2"


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


license_info["zed"] = "GNU AGPLv3"


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


license_info["ruff"] = "MIT License"
license_info["uv"] = "MIT License"


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


license_info["progit book"] = (
    "Creative Commons Attribution Non Commercial Share Alike 3.0"
)


@click.command
def progit():
    scratchspace = Path("scratchspace/progit")
    scratchspace.mkdir(exist_ok=True)

    extracted = dl_ex_zip(
        "https://github.com/progit/progit2/archive/refs/heads/main.zip",
        scratchspace / "progit2-main.zip",
    )
    collect("*.asc", extracted, Path("txts/git-progit2.txt"))


cli.add_command(progit)


license_info["zarr"] = "MIT License"


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

license_info["xarray"] = "Apache License 2.0"


@click.command
@click.option("--version")
def xarray(version: str | None):
    scratchspace = Path("scratchspace/xarray")
    scratchspace.mkdir(exist_ok=True)

    latest_version: str = version
    if version is None:
        latest_version = gh_latest_tag("pydata/xarray")

    ep(f"Downloading xarray {latest_version} source repo, collecting docs...")
    extracted = dl_ex_zip(
        f"https://github.com/pydata/xarray/archive/refs/tags/v{latest_version}.zip",
        scratchspace / latest_version / f"xarray-{latest_version}.zip",
    )
    txt_dest = Path(f"txts/xarray-{latest_version}.txt")
    collect("*.rst", extracted / "doc" / "user-guide", txt_dest)

    ep(f"Grabbing xarray's rendered api documentation and adding it to the txt...")
    resp = httpx.get(f"https://docs.xarray.dev/en/v{latest_version}/api.html")
    # filter out non doc html stuff
    soup = BeautifulSoup(resp.text, "lxml")
    soup = BeautifulSoup(
        str(list(soup.find_all("article", class_="bd-article"))[0]), "lxml"
    )
    for tag in soup.find_all("a"):
        tag.unwrap()
    text_maker = html2text.HTML2Text()
    text_maker.ignore_images = True
    converted = text_maker.handle(str(soup))
    with txt_dest.open(mode="a") as f:
        f.write(converted)

    ep(f"Done processing xarray {latest_version}")


cli.add_command(xarray)

license_info["icechunk"] = "Apache License 2.0"


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
    soup = BeautifulSoup(resp.text, "lxml")
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


license_info["mlx"] = "MIT License"


@click.command
@click.option("--version")
def mlx():
    scratchspace = Path("scratchspace/mlx")
    scratchspace.mkdir(exist_ok=True)

    # download the latest build from the github pages branch
    latest_version: str = version
    if version is None:
        latest_version = gh_latest_tag("earth-mover/icechunk")
    ep(f"Downloading mlx {latest_version} gh-pages build")
    extracted = dl_ex_zip(
        "https://github.com/ml-explore/mlx/archive/refs/heads/gh-pages.zip",
        scratchspace / latest_version / "mlx-gh-pages.zip",
    )
    with tempfile.NamedTemporaryFile(mode="w+", delete=True, suffix=".html") as fp:
        collected_html_p = Path(fp.name)
        ep(f"Collecting together and filtering the html into the final txt...")
        collect(
            "*.html", extracted / "docs" / "build" / "html" / "python", collected_html_p
        )
        soup = BeautifulSoup(collected_html_p.read_text(), "lxml")
        # Remove all anchor hrefs and leave just the content
        filtered = io.StringIO()
        for elem in soup.find_all("article", class_="bd-article"):
            filtered.write(str(elem))
        soup = BeautifulSoup(filtered.getvalue(), "lxml")
        for tag in soup.find_all("a"):
            tag.unwrap()
        text_maker = html2text.HTML2Text()
        text_maker.ignore_images = True
        converted = text_maker.handle(str(soup))

        txt_dest = Path(f"txts/mlx-{latest_version}.txt")
        with txt_dest.open(mode="w") as f:
            f.write(converted)

    ep(f"Done processing mlx {latest_version}")


cli.add_command(mlx)


def devdocs_clean_and_write(source: Path, txt_dest: Path):
    with tempfile.NamedTemporaryFile(mode="w+", delete=True, suffix=".html") as fp:
        collected_html_p = Path(fp.name)
        collect("*.html", source, collected_html_p)
        soup = BeautifulSoup(collected_html_p.read_text(), "lxml")

        # Clean up the context by removing unnecessary information
        elems_to_remove = soup.find_all("div", class_="_attribution")
        for elem in elems_to_remove:
            elem.decompose()
        # Clean up browser compatibility information from html/css docs to get under 25 MB
        browser_compat_tables = soup.find_all("table", class_="standard-table")
        for elem in browser_compat_tables:
            elem.decompose()
        # Remove all anchor hrefs and leave just the content
        for tag in soup.find_all("a"):
            tag.unwrap()

        text_maker = html2text.HTML2Text()
        text_maker.ignore_images = True
        converted = text_maker.handle(str(soup))
        with txt_dest.open(mode="w") as f:
            f.write(converted)


list_of_all_docs = json.load(httpx.get("https://devdocs.io/docs/docs.json"))


def devdocs(tool_name: str):
    @click.command(name=tool_name)
    @click.option("--version", help="Has to match the devdocs.io version available.")
    def f(version: str | None):
        scratchspace = Path(f"scratchspace/{tool_name}")
        scratchspace.mkdir(exist_ok=True)

        slug = tool_name
        if version is not None:
            slug = slug + "~" + version
        elif tool_name == "numpy":
            # If it's numpy and a version was not specified, we need to find the latest slug since numpy is not available as an alias for some reason
            versions = []
            for d in list_of_all_docs:
                if tool_name in d["slug"]:
                    versions.append(d["version"])
            latest_version = sorted(versions)[-1]
            slug = slug + "~" + latest_version

        ep(f"Downloading {slug} docs from devdocs")
        devdocs_dl(slug, scratchspace)

        meta_info = json.loads((scratchspace / "meta.json").read_text())
        version: str = "vNA"
        if "release" in meta_info:
            version = meta_info["release"]
        ep(f"Confirming downloaded {tool_name} {version} docs from devdocs")
        ep(f"Cleaning up html and parsing it into a collated txt")
        txt_dest = Path(f"txts/{tool_name}-{version}.txt")
        devdocs_clean_and_write(scratchspace, txt_dest)

        ep(f"Done processing {tool_name} {version}")

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

    # Write out
    Path("site-build/index.html").write_text(index_html.getvalue())
    ep("Copying over all txts for website static assets...")
    shutil.copytree(Path("txts"), Path("site-build/txts"), dirs_exist_ok=True)
    ep("Done with building website")


cli.add_command(build_site)
