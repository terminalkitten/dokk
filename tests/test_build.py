import hashlib
import re
import shutil
from pathlib import Path
from urllib.parse import unquote

import pytest

from dokk.build import build
from dokk.cli import main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "basic"
EVIL = "<script>alert(1)</script>"


def _files(out: Path) -> list[str]:
    return sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())


@pytest.fixture
def example(tmp_path: Path) -> Path:
    root = tmp_path / "basic"
    shutil.copytree(EXAMPLE, root, ignore=shutil.ignore_patterns("dist"))
    return root


def test_example_output_files(example: Path) -> None:
    out = build(example, search=False).out_dir
    files = _files(out)
    assert [f for f in files if not f.startswith("_dokk/")] == [
        ".nojekyll",
        "404.html",
        "getting-started/configuration/index.html",
        "getting-started/index.html",
        "getting-started/install/index.html",
        "guides/advanced/deep/nested/index.html",
        "guides/components/index.html",
        "guides/img/diagram.png",
        "guides/markdown/index.html",
        "guides/secret/index.html",  # hidden from the menu, still built
        "guides/writing/index.html",
        "index.html",
        "reference/café-ünïcode/index.html",
        "reference/index.html",
        "robots.txt",
        "sitemap.xml",
    ]
    for asset in ("dokk.css", "dokk.js", "pygments.css", "vendor/basecoat/basecoat.cdn.min.css"):
        assert f"_dokk/{asset}" in files


def test_drafts_flag(example: Path) -> None:
    out = build(example, search=False, drafts=True).out_dir
    assert (out / "reference/draft/index.html").is_file()


def test_current_page_and_open_submenu(example: Path) -> None:
    html = (
        build(example, search=False).out_dir / "guides/advanced/deep/nested/index.html"
    ).read_text()
    assert re.search(r'href="/guides/advanced/deep/nested/"\s*aria-current="page"', html)
    assert html.count('aria-current="page"') == 2  # menu item + breadcrumb
    assert len(re.findall(r"<details[^>]*\sopen", html)) == 2
    assert "secret" not in html.split("</aside>")[0]


def test_script_title_is_escaped_everywhere(make_site) -> None:
    root = make_site(
        {
            "index.md": "Home",
            "evil/index.md": f"---\ntitle: '{EVIL}'\ndescription: '\"{EVIL}'\n---\n",
            "evil/page.md": f"---\ntitle: '{EVIL}'\nsidebar:\n  badge: '{EVIL}'\n---\n",
            "evil/sub/deep.md": f"---\ntitle: '{EVIL}'\n---\n",
        }
    )
    out = build(root).out_dir
    for rel in ("evil/index.html", "evil/page/index.html", "evil/sub/deep/index.html"):
        html = (out / rel).read_text()
        assert "<script>alert" not in html, rel
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    html = (out / "evil/index.html").read_text()
    assert '<meta name="description" content="&#34;&lt;script&gt;' in html
    assert "<title>&lt;script&gt;" in html


def test_base_path_prefixes_every_internal_url(example: Path) -> None:
    toml = example / "dokk.toml"
    toml.write_text(toml.read_text().replace("https://example.com/", "https://example.com/repo/"))
    out = build(example, search=False).out_dir
    urls = set()
    for f in out.rglob("*.html"):
        urls |= set(re.findall(r'(?:href|src)="(/[^"]*)"', f.read_text()))
    assert urls, "no internal URLs found"
    assert {u for u in urls if not u.startswith("/repo/")} == set()
    assert "/repo/_dokk/dokk.css" in urls


@pytest.mark.parametrize("site_url", ["https://example.com/", "https://example.com/repo/"])
def test_every_internal_url_resolves(example: Path, site_url: str) -> None:
    toml = example / "dokk.toml"
    toml.write_text(toml.read_text().replace("https://example.com/", site_url))
    result = build(example, search=False)
    cfg, out = result.cfg, result.out_dir
    missing = set()
    for page in out.rglob("*.html"):
        for url in re.findall(r'(?:href|src)="(/[^"#]*)', page.read_text()):
            assert url.startswith(cfg.base_path + "/"), (page, url)
            target = out / unquote(url[len(cfg.base_path) + 1 :])
            if not (target.is_file() or (target / "index.html").is_file()):
                missing.add(url)
    assert missing == set()


def test_heading_ids_do_not_clash_with_layout(example: Path) -> None:
    html = (build(example, search=False).out_dir / "guides/markdown/index.html").read_text()
    ids = re.findall(r'\sid="([^"]+)"', html)
    assert len(ids) == len(set(ids))


def test_build_is_deterministic(example: Path, tmp_path: Path) -> None:
    def digest() -> dict[str, str]:
        out = build(example, search=False).out_dir
        return {f: hashlib.sha256((out / f).read_bytes()).hexdigest() for f in _files(out)}

    first = digest()
    assert digest() == first


def test_unknown_directive_fails_build_with_file_and_line(make_site, capsys) -> None:
    root = make_site({"index.md": "---\ntitle: Home\n---\n\n:::nope\nx\n:::\n"})
    assert main(["build", "--root", str(root)]) == 1
    assert "index.md: line 5: unknown directive ':::nope'" in capsys.readouterr().err


def test_public_dir_copied_to_root(make_site) -> None:
    root = make_site({"index.md": "Home"})
    (root / "public").mkdir()
    (root / "public" / "CNAME").write_text("docs.example.com")
    assert (build(root).out_dir / "CNAME").read_text() == "docs.example.com"


def test_custom_404_page(make_site) -> None:
    root = make_site({"index.md": "Home", "404.md": "# Lost\n\nNothing here."})
    out = build(root).out_dir
    html = (out / "404.html").read_text()
    assert "<h1>Lost</h1>" in html and "Nothing here." in html
    assert not (out / "404").exists()


def test_user_template_overrides_builtin(make_site) -> None:
    root = make_site({"index.md": "Home"})
    (root / "templates" / "partials").mkdir(parents=True)
    (root / "templates" / "partials" / "pager.html.jinja").write_text("<p>CUSTOM PAGER</p>")
    assert "CUSTOM PAGER" in (build(root).out_dir / "index.html").read_text()


def test_cli_build_and_error(make_site, capsys: pytest.CaptureFixture[str]) -> None:
    root = make_site({"a_b.md": "A", "a-b.md": "B"})
    assert main(["build", "--root", str(root)]) == 1
    assert "route /a-b/ is produced by both" in capsys.readouterr().err


def test_cli_init_then_build(tmp_path: Path) -> None:
    assert main(["init", "--root", str(tmp_path)]) == 0
    workflow = (tmp_path / ".github" / "workflows" / "docs.yml").read_text()
    assert "actions/deploy-pages@v5" in workflow and "dokk check" in workflow
    assert main(["build", "--root", str(tmp_path)]) == 0
    assert (tmp_path / "dist" / "index.html").is_file()
    assert main(["init", "--root", str(tmp_path)]) == 1  # refuses to overwrite


def test_parallel_markdown_matches_serial(example: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import dokk.build as build_module

    def snapshot(**kw: object) -> dict[str, bytes]:
        out = build(example, search=False, **kw).out_dir  # type: ignore[arg-type]
        return {f: (out / f).read_bytes() for f in _files(out)}

    serial = snapshot()
    monkeypatch.setattr(build_module, "PARALLEL_MIN_PAGES", 0)
    assert snapshot(parallel=True) == serial
