# [Website with prebuilt txts](https://llms-txts.abidsikder.com/)

# llms-txts
Creating missing llms.txts. Hoping to work with the open source community to fan out for other documentation sets.

# Environment requirements
+ curl
+ [code2prompt](https://github.com/mufeedvh/code2prompt)
+ [uv](https://github.com/astral-sh/uv)

> [!NOTE]
> Invocations of the CLI `lt` must happen from the repo root. It simplifies the code to make this assumption.

# Generate txts
See the list of documentation sets available with `uv run lt --help`. See `doall.sh` for a shell script that will build all of them at once.

# Generate the website
```
uv run lt build-site
```
This will place the static website in `site-build/`.

# Licensing
License acknowledgements for documentation texts are included in the website. The repo code itself is under the MIT License.
