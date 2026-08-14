#!/usr/bin/env python3
"""Build the restored Livgently archive as a dependency-free static site."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
SITE_URL = "https://mgrang.github.io/static-publishing"
DESCRIPTION = "A restored archive of thoughtful stories about language, life, travel, money, and finding delight in the everyday."


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def layout(*, title: str, description: str, content: str, depth: int = 0, image: str = "/og.png", page_url: str = "/") -> str:
    prefix = "../" * depth
    absolute_image = f"{SITE_URL}{image}"
    absolute_url = f"{SITE_URL}{page_url}"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{absolute_url}">
  <link rel="icon" href="{prefix}livgently-icon.png">
  <link rel="stylesheet" href="{prefix}style.css">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Livgently">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{absolute_url}">
  <meta property="og:image" content="{absolute_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{absolute_image}">
</head>
<body>
  <header class="site-header">
    <a class="brand" href="{prefix}index.html" aria-label="Livgently home"><img src="{prefix}livgently-logo.png" alt="Livgently"></a>
    <nav aria-label="Primary navigation"><a href="{prefix}index.html#stories">Stories</a><a href="{prefix}about/">About</a></nav>
  </header>
  {content}
  <footer><img src="{prefix}livgently-logo.png" alt="Livgently"><p>Think deeply. Give freely. Live gently.</p><small>An independent publication, restored from its original 2016–2017 archive.</small></footer>
</body>
</html>
"""


def home(posts: list[dict]) -> str:
    featured, *archive = posts
    cards = []
    for index, post in enumerate(archive):
        wide = " wide" if index == 0 else ""
        cards.append(f"""<article class="post-card{wide}">
  <a class="card-image" href="{post['slug']}/"><img src=".{post['hero']}" alt="" loading="lazy"></a>
  <div class="card-copy"><p class="category">{esc(post['category'])}</p><h3><a href="{post['slug']}/">{esc(post['title'])}</a></h3><p>{esc(post['excerpt'])}</p>
  <div class="card-meta"><time>{esc(post['date'])}</time><a href="{post['slug']}/" aria-label="Read {esc(post['title'])}">Read →</a></div></div>
</article>""")
    return f"""<main>
<section class="hero-wrap"><a class="featured" href="{featured['slug']}/"><img src=".{featured['hero']}" alt=""><div class="featured-copy"><p class="kicker">A gently restored archive</p><p class="category">{esc(featured['category'])}</p><h1>{esc(featured['title'])}</h1><p class="dek">{esc(featured['excerpt'])}</p><span class="read-link">Read the story →</span></div></a></section>
<section class="archive" id="stories"><div class="section-heading"><div><p class="kicker">From the original 2016–2017 publication</p><h2>The archive</h2></div><p>Ideas for living with more curiosity, intention, and delight—recovered from the original Livgently backup.</p></div><div class="post-grid">{''.join(cards)}</div></section>
</main>"""


def story(post: dict, next_post: dict) -> str:
    blocks = []
    for block in post["blocks"]:
        kind = block["type"]
        if kind == "image":
            blocks.append(f'<figure class="inline-image"><img src="..{esc(block["src"])}" alt="{esc(block["alt"])}" loading="lazy"></figure>')
        elif kind == "heading":
            blocks.append(f'<h2>{esc(block["text"])}</h2>')
        elif kind == "quote":
            blocks.append(f'<blockquote>{esc(block["text"])}</blockquote>')
        else:
            blocks.append(f'<p>{esc(block["text"])}</p>')
    return f"""<main class="story-page"><article>
<header class="story-header"><a class="back-link" href="../index.html#stories">← All stories</a><p class="category">{esc(post['category'])}</p><h1>{esc(post['title'])}</h1><p class="story-dek">{esc(post['excerpt'])}</p><div class="byline"><span>By {esc(post['author'])}</span><time>{esc(post['date'])}</time></div></header>
<figure class="story-hero"><img src="..{esc(post['hero'])}" alt=""></figure><div class="story-body">{''.join(blocks)}</div>
</article><aside class="next-story"><p class="kicker">Keep reading</p><a href="../{next_post['slug']}/">{esc(next_post['title'])} →</a></aside></main>"""


def about() -> str:
    return """<main class="about-page"><p class="kicker">About the publication</p><h1>Think deeply.<br>Give freely.<br><em>Live gently.</em></h1><div class="about-copy"><p>Livgently began in 2016 as an independent place for ideas worth carrying into everyday life—stories about language, travel, wellbeing, money, and the small choices that shape us.</p><p>This edition has been carefully reconstructed from the publication’s original backup. The words and photography belong to that first chapter; the presentation has been rebuilt for a faster, quieter, and more readable web.</p><p><a class="read-link" href="../index.html#stories">Explore the archive →</a></p></div></main>"""


def main() -> None:
    posts = json.loads((ROOT / "content" / "posts.json").read_text())
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "public", OUT)
    shutil.copy2(ROOT / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").touch()
    (OUT / "index.html").write_text(layout(title="Livgently", description=DESCRIPTION, content=home(posts)))
    about_dir = OUT / "about"
    about_dir.mkdir()
    (about_dir / "index.html").write_text(layout(title="About — Livgently", description="The story of Livgently and its restored independent archive.", content=about(), depth=1, page_url="/about/"))
    for index, post in enumerate(posts):
        target = OUT / post["slug"]
        target.mkdir()
        title = f"{post['title']} — Livgently"
        page = layout(title=title, description=post["excerpt"], content=story(post, posts[(index + 1) % len(posts)]), depth=1, image=post["hero"], page_url=f"/{post['slug']}/")
        (target / "index.html").write_text(page)
    (OUT / "404.html").write_text(layout(title="Page not found — Livgently", description=DESCRIPTION, content='<main class="about-page"><h1>Page not found.</h1><div class="about-copy"><p><a class="read-link" href="./index.html">Return home →</a></p></div></main>'))
    urls = [SITE_URL + "/", SITE_URL + "/about/"] + [f"{SITE_URL}/{post['slug']}/" for post in posts]
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")


if __name__ == "__main__":
    main()
