from pathlib import Path

from dokk.build import build
from dokk.check import check

SIDEBAR_TOML = """title = "T"
description = "Docs for T"
site_url = "https://x.io/t/"

[[sidebar]]
label = "Start"
items = ["index.md", { page = "intro.md", label = "Introduction" }]

[[sidebar]]
autogenerate = "guides"

[[sidebar]]
label = "Links"
items = [{ label = "GitHub", link = "https://github.com/x/t" }]

[llms]
enabled = true
"""

FILES = {
    "index.md": "---\ntitle: Home\ndescription: Start here\n---\nWelcome.\n",
    "intro.md": "# Intro\n\nIntro text.\n",
    "guides/index.md": "---\ntitle: Guides\n---\n",
    "guides/a.md": "---\ntitle: Guide A\n---\nBody of A with :::note markers left as is.\n",
    "orphan.md": "# Orphan\n",
    "secret.md": "---\ntitle: Secret\nnoindex: true\nsidebar:\n  hidden: true\n---\nHidden.\n",
}


def test_configured_sidebar_in_html(make_site) -> None:
    out = build(make_site(FILES, SIDEBAR_TOML)).out_dir
    html = (out / "guides/a/index.html").read_text()
    nav = html.split("</aside>")[0]
    assert '<h3 id="group-label-dk-sidebar-content-1">Start</h3>' in nav
    assert "<span>Introduction</span>" in nav
    assert '<a href="/t/guides/a/" aria-current="page"' in nav
    assert 'href="https://github.com/x/t"' in nav
    assert "Orphan" not in nav
    assert (out / "orphan/index.html").is_file()  # still built
    assert 'rel="next" href' not in html  # pager follows the sidebar: A is the last page
    assert '<a class="dk-pager-prev" href="/t/guides/"' in html


def test_check_warns_about_pages_missing_from_sidebar(make_site) -> None:
    issues = [str(i) for i in check(make_site(FILES, SIDEBAR_TOML))]
    assert "warning: orphan.md: not in the sidebar (add it, or set sidebar.hidden: true)" in issues
    assert not any("secret.md: not in the sidebar" in i for i in issues)  # hidden on purpose


def test_llms_txt(make_site) -> None:
    out = build(make_site(FILES, SIDEBAR_TOML)).out_dir
    assert (out / "llms.txt").read_text() == (
        "# T\n\n> Docs for T\n\n"
        "## Start\n\n"
        "- [Home](https://x.io/t/): Start here\n"
        "- [Intro](https://x.io/t/intro/): Intro text.\n\n"
        "## Guides\n\n"
        "- [Guides](https://x.io/t/guides/)\n"
        "- [Guide A](https://x.io/t/guides/a/): Body of A with :::note markers left as is.\n"
    )
    full = (out / "llms-full.txt").read_text()
    assert full.startswith("# T\n")
    assert "# Guide A\n\nURL: https://x.io/t/guides/a/\n\nBody of A" in full
    assert full.index("# Home") < full.index("# Guide A") < full.index("# Orphan")
    assert "Secret" not in full  # noindex pages are left out


def test_llms_off_by_default(make_site) -> None:
    out = build(make_site({"index.md": "x"})).out_dir
    assert not (out / "llms.txt").exists() and not (out / "llms-full.txt").exists()


def test_build_speed(tmp_path: Path, make_site) -> None:
    """Regression alarm (PLAN.md section 7): 300 rich pages, serial, well under the budget."""
    import time

    body = "## H\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n```python\nx = 1\n```\n\n:::note\nhi\n:::\n"
    files = {f"s{i % 10}/p{i}.md": f"---\ntitle: P{i}\n---\n{body}" for i in range(300)}
    root = make_site(files)
    start = time.perf_counter()
    build(root)
    assert time.perf_counter() - start < 5  # about 0.5 s on a laptop
