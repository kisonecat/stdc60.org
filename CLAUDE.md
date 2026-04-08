# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hakyll-based static site generator for the 60th Spring Topology and Dynamics Conference (STDC 60). Built with Haskell and Nix, deployed to GitHub Pages.

## Build & Development Commands

### Using Nix (recommended, reproducible)

```bash
nix build                   # Build the site executable
nix run . -- build          # Generate static site into _site/
nix run .#watch             # Live-reload dev server (watches for changes)
```

### Using Cabal directly

```bash
cabal build                 # Build the site executable
cabal run site -- build     # Generate static site into _site/
cabal run site -- watch     # Live-reload dev server
cabal run site -- clean     # Remove _site/ and _cache/
```

The dev shell (enter with `nix develop`) includes: cabal-install, haskell-language-server, ghcid, Hoogle.

## Architecture

### Hakyll Pipeline (`site.hs`)

The site compiler does three things:
1. Copies `css/*.css` as-is
2. Compiles `content/**/*.md` → HTML via Pandoc, applies `templates/page.html` then `templates/default.html`, and relativizes URLs. The routing strips the `content/` prefix so `content/foo.md` becomes `foo.html`.
3. Compiles Hakyll templates from `templates/`

### Content

All content lives in `content/` as Markdown files with YAML front matter (`title` field used by templates). Research track pages are under `content/tracks/`.

### Templates

- `templates/default.html` — full page layout with nav, header, footer, and KaTeX CDN for math rendering
- `templates/page.html` — article wrapper that injects `$title$` and `$body$`

### Output

- `_site/` — generated static HTML (git-ignored, deployed by CI)
- `_cache/` — Hakyll build cache (git-ignored)

## Deployment

GitHub Actions (`.github/workflows/deploy.yml`) builds with GHC 9.6 via `cabal build` + `cabal run site -- build`, then deploys `_site/` to GitHub Pages using the official Pages API. Triggered on push to `main`.
