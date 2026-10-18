import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from functools import partial
from http.server import ThreadingHTTPServer

import pytest

from dokk.serve import DevHandler, DevState, is_input, watch_paths


@pytest.fixture
def server(make_site) -> Iterator[tuple[str, DevState]]:
    root = make_site(
        {
            "index.md": "---\ntitle: Home\n---\nHello\n",
            "wip.md": "---\ntitle: WIP\ndraft: true\n---\n",
        },
        'title = "T"\nsite_url = "https://x.io/repo/"\n',
    )
    state = DevState(root)
    state.rebuild()
    handler = type("Handler", (DevHandler,), {"state": state})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(handler, directory=str(state.out)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}", state
    httpd.shutdown()
    httpd.server_close()


def _get(url: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def test_dev_build(server: tuple[str, DevState]) -> None:
    base, state = server
    status, html = _get(base + "/")
    assert status == 200
    assert 'href="/_dokk/dokk.css"' in html  # base_path dropped in dev
    assert "/__dokk/version" in html  # reload script injected
    assert _get(base + "/wip/")[0] == 200  # drafts included
    assert state.out == state.root / ".dokk" / "dev"
    assert not (state.root / ".dokk" / "build").exists()


def test_rebuild_keeps_serving_the_old_site(server: tuple[str, DevState], monkeypatch) -> None:
    base, state = server
    import dokk.build as build_module

    real_copy = build_module.copy_static

    def copy_static(*args, **kwargs):  # runs after the build cleared its output folder
        assert _get(base + "/")[0] == 200  # mid-rebuild: the old site is still served
        return real_copy(*args, **kwargs)

    monkeypatch.setattr(build_module, "copy_static", copy_static)
    state.rebuild()
    assert state.error is None and _get(base + "/")[0] == 200
    assert sorted(p.name for p in state.out.parent.iterdir()) == ["dev"]


def test_version_increments_on_rebuild(server: tuple[str, DevState]) -> None:
    base, state = server
    assert _get(base + "/__dokk/version") == (200, "1")
    state.rebuild()
    assert _get(base + "/__dokk/version") == (200, "2")


def test_error_page_and_recovery(server: tuple[str, DevState]) -> None:
    base, state = server
    page = state.root / "docs" / "index.md"
    page.write_text("---\ntitle: [oops\n---\n")
    state.rebuild()
    status, html = _get(base + "/")
    assert status == 500
    assert "invalid front matter" in html and "/__dokk/version" in html

    page.write_text("---\ntitle: Fixed\n---\n")
    state.rebuild()
    status, html = _get(base + "/")
    assert status == 200 and "Fixed" in html


def test_404_uses_site_page(server: tuple[str, DevState]) -> None:
    base, _ = server
    status, html = _get(base + "/nope/")
    assert status == 404 and "Page not found" in html


def test_production_build_has_no_reload_script(make_site) -> None:
    from dokk.build import build

    root = make_site({"index.md": "x"})
    assert "__dokk" not in (build(root).out_dir / "index.html").read_text()


def test_watched_inputs(make_site) -> None:
    root = make_site({"index.md": "x"}).resolve()
    inputs = watch_paths(root)
    for rel in ("dokk.toml", "docs/a.md", "templates/x.html.jinja", "public/CNAME"):
        assert is_input(root / rel, inputs), rel
    for rel in (".dokk/dev/index.html", "dist/index.html", "README.md", ".git/HEAD"):
        assert not is_input(root / rel, inputs), rel
