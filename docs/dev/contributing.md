# Contributing Guide

See [CONTRIBUTING.md](https://github.com/TanjunBot/new_tanjun/blob/development/CONTRIBUTING.md) in the repository root for the full contributing guide.

## Quick Start

```bash
git clone https://github.com/TanjunBot/new_tanjun.git
cd new_tanjun
python3.12 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your configuration
python main.py
```

## Building the Docs

This documentation site is built with [MkDocs](https://www.mkdocs.org/) and the Material theme.

```bash
pip install mkdocs mkdocs-material mkdocstrings
mkdocs serve
```

This will start a local preview server at `http://127.0.0.1:8000`.

## Adding a Page

1. Create a new `.md` file in the relevant `docs/` subdirectory.
2. Add it to the `nav` section in `mkdocs.yml`.

## API Reference

The API reference is auto-generated from Python docstrings using [mkdocstrings](https://mkdocstrings.github.io/). Add Google-style docstrings to your code and they will appear in the reference automatically.
