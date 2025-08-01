Live website for easy access: [llm-txts.pages.dev](https://llm-txts.pages.dev/)
===

# llm-txts
These are llms.txts for projects that don't have them. I like using as much context as possible and doing ad-hoc semantic search on library documentation. I found myself duplicating work after constructing these sorts of things multiple times over, so I'm creating tools to automate the process and hopefully work with the open source community to fan out over the possibilities.

# Dev environment requirements
+ code2prompt
+ uv, uvx
+ fd

> [!NOTE]
> Following invocations of the CLI must happen from the repo root. It simplifies the code a fair bit to make this assumption.

# Generate txts
See the list of commands with `uv run lt --help`. In general, they will place a complete .txt file in `txts/`.

# Generate the website
```
uv run lt build-site
```
This will place a simple static website in `site-build/`.

TODO make the workflow in cli.py for the Javascript from devdocs (in a way that strips out the lines after the copyright symbols in files, to maximize context usage. Reuse this for a bunch of the other common devdocs


fd -e html --exec bash -c "html2text {} > {.}.txt"
