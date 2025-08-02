Live website for easy access: [llm-txts.pages.dev](https://llm-txts.pages.dev/)
===

# llm-txts
These are llms.txts for projects that don't have them. I like using as much context as possible and doing ad-hoc semantic search on library documentation. I found myself duplicating work after constructing these sorts of things multiple times over, so I'm creating tools to automate the process and hopefully work with the open source community to fan out for other documentation sets.

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
