import gzip
import os
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest

from dokk.build import build
from dokk.check import heading_issues
from dokk.content import Page
from dokk.search import search_available
from dokk.seo import last_modified, robots, sitemap

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "basic"


def test_sitemap_xml() -> None:
    xml = sitemap([("https://x.io/a&b/", date(2026, 1, 2)), ("https://x.io/", None)])
    assert "<loc>https://x.io/a&amp;b/</loc><lastmod>2026-01-02</lastmod>" in xml
    assert "<url><loc>https://x.io/</loc></url>" in xml
    assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns=')


def test_robots() -> None:
    assert robots("https://x.io/sitemap.xml").endswith("Sitemap: https://x.io/sitemap.xml\n")
    assert "Sitemap" not in robots("")


def _git(cwd: Path, *args: str, when: str = "2026-03-04T12:00:00") -> None:
    env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=env)


def test_last_modified_from_git_then_mtime(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    (docs / "sub").mkdir(parents=True)
    for rel in ("a.md", "sub/café.md", "new.md"):
        (docs / rel).write_text(rel)
    os.utime(docs / "new.md", (0, 86400 * 365))
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "add", "docs/a.md", "docs/sub")
    _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
    pages = [
        Page(src=docs / r, rel=Path(r), meta={}, body="") for r in ("a.md", "sub/café.md", "new.md")
    ]
    dates = last_modified(docs, pages)
    assert dates[Path("a.md")] == date(2026, 3, 4)
    assert dates[Path("sub/café.md")] == date(2026, 3, 4)  # unicode path, not quoted
    assert dates[Path("new.md")] == date.fromtimestamp(86400 * 365)  # untracked: mtime


def test_seo_output(make_site) -> None:
    root = make_site(
        {
            "index.md": "---\ntitle: Home\ndescription: The home page\n---\nHi\n",
            "café.md": "---\ntitle: Café\n---\nx\n",
            "secret.md": "---\ntitle: S\nnoindex: true\n---\nx\n",
        },
        'title = "T"\nsite_url = "https://x.io/repo/"\n'
        '[links]\nedit_url = "https://gh.io/e/docs/{path}"\n',
    )
    (root / "public").mkdir()
    (root / "public" / "favicon.svg").write_text("<svg/>")
    out = build(root).out_dir
    home = (out / "index.html").read_text()
    assert '<meta property="og:title" content="Home">' in home
    assert '<meta property="og:description" content="The home page">' in home
    assert '<meta property="og:url" content="https://x.io/repo/">' in home
    assert '<meta property="og:type" content="website">' in home
    assert '<link rel="icon" href="/repo/favicon.svg">' in home
    assert 'name="theme-color"' in home
    assert 'href="https://gh.io/e/docs/index.md">Edit this page</a>' in home
    assert re.search(r'Last updated <time datetime="\d{4}-\d\d-\d\d">', home)

    cafe = (out / "café/index.html").read_text()
    assert 'href="https://gh.io/e/docs/caf%C3%A9.md"' in cafe
    assert '<link rel="canonical" href="https://x.io/repo/caf%C3%A9/">' in cafe
    assert '<meta name="robots" content="noindex">' in (out / "secret/index.html").read_text()

    xml = (out / "sitemap.xml").read_text()
    assert re.findall(r"<loc>([^<]+)</loc>", xml) == [
        "https://x.io/repo/",
        "https://x.io/repo/caf%C3%A9/",
    ]
    assert (out / "robots.txt").read_text().endswith("Sitemap: https://x.io/repo/sitemap.xml\n")


def test_no_site_url_means_no_sitemap(make_site) -> None:
    out = build(make_site({"index.md": "x"})).out_dir
    assert not (out / "sitemap.xml").exists()
    assert (out / "robots.txt").read_text() == "User-agent: *\nAllow: /\n"


def test_public_robots_wins(make_site) -> None:
    root = make_site({"index.md": "x"}, 'title = "T"\nsite_url = "https://x.io/"\n')
    (root / "public").mkdir()
    (root / "public" / "robots.txt").write_text("custom")
    assert (build(root).out_dir / "robots.txt").read_text() == "custom"


@pytest.mark.parametrize(
    ("article", "expected"),
    [
        ("<h1>T</h1><h2 id=a>A</h2><h3>B</h3><h2>C</h2>", []),
        ("<h1>T</h1><h1>Again</h1>", ["expected one <h1>, found 2"]),
        ("<h1>T</h1><h2>A</h2><h4>B</h4>", ["heading level skipped: h2 to h4"]),
        ("<h1>T</h1><h3>B</h3>", ["heading level skipped: h1 to h3"]),
    ],
)
def test_heading_issues(article: str, expected: list[str]) -> None:
    html = f'<h2>outside</h2><article class="dk-prose">{article}</article><h5>x</h5>'
    assert [i.message for i in heading_issues("p.md", html)] == expected


def test_search_disabled_by_config(make_site) -> None:
    result = build(make_site({"index.md": "x"}))
    assert not result.search and not result.search_missing
    html = (result.out_dir / "index.html").read_text()
    assert "dk-search" not in html and not (result.out_dir / "pagefind").exists()


@pytest.mark.skipif(not search_available(), reason="pagefind not installed (search extra)")
def test_search_index_and_ui(tmp_path: Path) -> None:
    root = tmp_path / "basic"
    shutil.copytree(EXAMPLE, root, ignore=shutil.ignore_patterns("dist", ".dokk"))
    toml = root / "dokk.toml"
    toml.write_text(toml.read_text().replace("https://example.com/", "https://example.com/repo/"))
    result = build(root)
    assert result.search
    out = result.out_dir
    assert (out / "pagefind" / "pagefind-ui.js").is_file()
    html = (out / "index.html").read_text()
    assert 'data-bundle="/repo/pagefind/" data-base="/repo/"' in html
    assert "data-dk-search" in html
    hits = [
        gzip.decompress(f.read_bytes())
        for f in (out / "pagefind" / "fragment").glob("*.pf_fragment")
        if b"zygomorphic" in gzip.decompress(f.read_bytes())
    ]
    assert len(hits) == 1 and b'"url":"/guides/advanced/deep/nested/"' in hits[0]
    first = {p: p.read_bytes() for p in (out / "pagefind").rglob("*") if p.is_file()}
    out2 = build(root).out_dir
    assert {p: p.read_bytes() for p in (out2 / "pagefind").rglob("*") if p.is_file()} == first
