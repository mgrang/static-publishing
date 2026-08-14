# Static Publishing

A shared repository for lightweight, independently published static sites.

## Sites

- **Livgently** — restored archive of the original 2016–2017 publication

Each publication lives under `sites/<site-name>` and owns its build script and source assets. The current GitHub Pages deployment builds Livgently from `sites/livgently`.

## Build locally

```bash
python sites/livgently/build_static.py
python -m http.server 4173 --directory sites/livgently/_site
```
