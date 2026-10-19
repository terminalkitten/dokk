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
from dokk.render import base_env, render_template
from dokk.search import search_available
from dokk.seo import last_modified

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "basic"


def test_sitemap_template() -> None:
    entries = [("https://x.io/a&b/", date(2026, 1, 2)), ("https://x.io/", None)]
    xml = render_template(base_env(), "files/sitemap.xml.jinja", entries=entries)
    assert "<loc>https://x.io/a&amp;b/</loc><lastmod>2026-01-02</lastmod>" in xml
    assert "<url><loc>https://x.io/</loc></url>" in xml
    assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns=')


def test_robots_template() -> None:
    def robots(url: str) -> str:
        return render_template(base_env(), "files/robots.txt.jinja", sitemap_url=url)

    assert robots("https://x.io/sitemap.xml").endswith("Sitemap: https://x.io/sitemap.xml\n")
    assert robots("") == "User-agent: *\nAllow: /\n"


def _git(cwd: Path, *args: str, when: str = "2026-03-04T12:00:00") -> None:
    env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=env)


def test_last_modified_from_git_then_mtime(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    (docs / "sub").mkdir(parents=True)
    for rel in ("a.md", "sub/café.md", "new.md"):
        (docs / rel).write_text(rel, encoding="utf-8")
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
    (root / "public" / "favicon.svg").write_text("<svg/>", encoding="utf-8")
    out = build(root).out_dir
    home = (out / "index.html").read_text(encoding="utf-8")
    assert '<meta property="og:title" content="Home">' in home
    assert '<meta property="og:description" content="The home page">' in home
    assert '<meta property="og:url" content="https://x.io/repo/">' in home
    assert '<meta property="og:type" content="website">' in home
    assert '<link rel="icon" href="/repo/favicon.svg">' in home
    assert 'name="theme-color"' in home
    assert 'href="https://gh.io/e/docs/index.md">Edit this page</a>' in home
    assert re.search(r'Last updated <time datetime="\d{4}-\d\d-\d\d">', home)

    cafe = (out / "café/index.html").read_text(encoding="utf-8")
    assert 'href="https://gh.io/e/docs/caf%C3%A9.md"' in cafe
    assert '<link rel="canonical" href="https://x.io/repo/caf%C3%A9/">' in cafe
    assert '<meta name="robots" content="noindex">' in (out / "secret/index.html").read_text(
        encoding="utf-8"
    )

    xml = (out / "sitemap.xml").read_text(encoding="utf-8")
    assert re.findall(r"<loc>([^<]+)</loc>", xml) == [
        "https://x.io/repo/",
        "https://x.io/repo/caf%C3%A9/",
    ]
    assert (
        (out / "robots.txt")
        .read_text(encoding="utf-8")
        .endswith("Sitemap: https://x.io/repo/sitemap.xml\n")
    )


def test_no_site_url_means_no_sitemap(make_site) -> None:
    out = build(make_site({"index.md": "x"})).out_dir
    assert not (out / "sitemap.xml").exists()
    assert (out / "robots.txt").read_text(encoding="utf-8") == "User-agent: *\nAllow: /\n"


def test_public_robots_wins(make_site) -> None:
    root = make_site({"index.md": "x"}, 'title = "T"\nsite_url = "https://x.io/"\n')
    (root / "public").mkdir()
    (root / "public" / "robots.txt").write_text("custom", encoding="utf-8")
    assert (build(root).out_dir / "robots.txt").read_text(encoding="utf-8") == "custom"


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
    html = (result.out_dir / "index.html").read_text(encoding="utf-8")
    assert "dk-search" not in html and not (result.out_dir / "pagefind").exists()


@pytest.mark.skipif(not search_available(), reason="pagefind not installed (search extra)")
def test_search_index_and_ui(tmp_path: Path) -> None:
    root = tmp_path / "basic"
    shutil.copytree(EXAMPLE, root, ignore=shutil.ignore_patterns("dist", ".dokk"))
    toml = root / "dokk.toml"
    toml.write_text(
        toml.read_text(encoding="utf-8").replace(
            "https://example.com/", "https://example.com/repo/"
        ),
        encoding="utf-8",
    )
    result = build(root)
    assert result.search
    out = result.out_dir
    assert (out / "pagefind" / "pagefind-ui.js").is_file()
    html = (out / "index.html").read_text(encoding="utf-8")
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


def test_style_and_color_theme(make_site) -> None:
    toml = 'title = "T"\n[theme]\nstyle = "rhea"\nbase = "zinc"\ncolor = "pink"\n'
    out = build(make_site({"index.md": "x"}, toml)).out_dir
    css = (out / "_dokk" / "theme.css").read_text(encoding="utf-8")
    light, dark = css.split(".dark {")
    assert "--background: oklch(1 0 0);" in light  # from the zinc base
    assert "--primary: oklch(0.525 0.223 3.958);" in light  # pink accent, light
    assert "--primary: oklch(0.459 0.187 3.815);" in dark  # pink accent, dark
    assert "--chart-2: oklch(0.656 0.241 354.308);" in light
    assert "--radius" not in css  # shape belongs to the style pack
    vendor = sorted(p.name for p in (out / "_dokk" / "vendor" / "basecoat").glob("*.css"))
    assert vendor == ["basecoat-rhea.cdn.min.css"]  # only the chosen style pack ships
    html = (out / "index.html").read_text(encoding="utf-8")
    order = [html.index(n) for n in ("basecoat-rhea.cdn.min.css", "theme.css", "dokk.css")]
    assert order == sorted(order)  # theme after the style pack, as Basecoat documents


def test_logo_from_public(make_site) -> None:
    root = make_site({"index.md": "x"}, 'title = "<T>"\nsite_url = "https://x.io/repo/"\n')
    out = build(root).out_dir
    assert "dk-logo" not in (out / "index.html").read_text(encoding="utf-8")  # no logo, title only

    (root / "public").mkdir()
    (root / "public" / "logo.svg").write_text("<svg/>", encoding="utf-8")
    html = (build(root).out_dir / "index.html").read_text(encoding="utf-8")
    logo = '<img class="dk-logo" src="/repo/logo.svg" alt="">'
    assert html.count(logo) == 2  # top bar and sidebar header
    assert html.count("<span>&lt;T&gt;</span>") == 2

    (root / "public" / "logo-dark.svg").write_text("<svg/>", encoding="utf-8")
    html = (build(root).out_dir / "index.html").read_text(encoding="utf-8")
    assert html.count('<img class="dk-logo dk-logo-light" src="/repo/logo.svg" alt="">') == 2
    assert html.count('<img class="dk-logo dk-logo-dark" src="/repo/logo-dark.svg" alt="">') == 2
