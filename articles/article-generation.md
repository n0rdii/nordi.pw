---
title: "How I generate articles on GitHub Pages"
date: "2026-08-28"
description: "Using a Python script to convert Markdown to styled HTML pages."
tags: [meta, python, web]
---

# How I generate articles on GitHub Pages

This site runs on GitHub Pages — static hosting, no backend. But I wanted to write articles in Markdown and have them render in my site's style.

## The workflow

1. Write a `.md` file in `articles/` with YAML frontmatter
2. Run `python3 build.py`
3. The script generates a styled `.html` file in `dist/`

## The script

The `build.py` script:

- Parses frontmatter (title, date, tags, description)
- Converts Markdown to HTML (headings, bold, code blocks, lists, links)
- Wraps it in the same dark theme CSS as the main site
- Generates `dist/index.json` for the blog listing with search and tag filtering

A new article is just a new `.md` file and one command.
