Live website for easy access: [llm-txts.pages.dev](https://llm-txts.pages.dev/)
===

# llms-txts
These are llms.txt for projects that don't have them. I found myself creating these things multiple times over on an ad-hoc basis—now I'm creating tools to automate the process and hopefully work with the open source community to fan out for other documentation sets.

# Environment requirements
+ [code2prompt](https://github.com/mufeedvh/code2prompt)
+ [uv](https://github.com/astral-sh/uv)

> [!NOTE]
> Invocations of the CLI `lt` must happen from the repo root. It simplifies the code to make this assumption.

# Generate txts
See the list of documentation sets available with `uv run lt --help`. In general, they will place a complete .txt file in `txts/`.

# Generate the website
```
uv run lt build-site
```
This will place the static website in `site-build/`.
