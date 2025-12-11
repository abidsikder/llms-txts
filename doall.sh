#!/bin/bash
set -e # exit immediately on any errors

echo "Building all documentation sets in parallel" >&2
uv run lt bash &
uv run lt beautifulsoup &
uv run lt boto3 &
uv run lt click &
uv run lt commanderjs &
uv run lt css &
uv run lt dom &
uv run lt git &
uv run lt homebrew &
uv run lt html &
uv run lt hy &
uv run lt icechunk &
uv run lt javascript &
uv run lt jq &
uv run lt mlx &
uv run lt networkx &
uv run lt nodejs 22 &
uv run lt nodejs 23 &
uv run lt nodejs 24 &
uv run lt numpy &
uv run lt p5js &
uv run lt progit &
uv run lt puppeteer &
uv run lt python 3.10 &
uv run lt python 3.11 &
uv run lt python 3.12 &
uv run lt python 3.13 &
# uncomment after release in 2025-10-07
# uv run lt python 3.14 &
uv run lt pytorch &
uv run lt ruff &
uv run lt svelte &
uv run lt ty &
uv run lt typescript &
uv run lt typst &
uv run lt uv &
uv run lt vite &
uv run lt vitest &
uv run lt whenever &
uv run lt xarray --version "2025.07.1" &
uv run lt zarr &
uv run lt zed &
uv run lt zig language 0.15.2 &
uv run lt zig language master &
uv run lt zsh &

echo "Finished building all documentation sets" >&2

# when wait is called without a pid, it waits until all background child processes are done
wait
uv run lt build-site

echo "Finished building website" >&2
