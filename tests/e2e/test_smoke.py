"""Browser smoke tests. Need the e2e extra plus `playwright install chromium`."""

import os
import shutil
import threading
from collections.abc import Iterator
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from dokk.build import build
from dokk.search import search_available

playwright = pytest.importorskip("playwright.sync_api")

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "basic"
SHOTS = os.environ.get("DOKK_SCREENSHOTS")  # optional folder for screenshots


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    root = tmp_path_factory.mktemp("e2e") / "basic"
    shutil.copytree(EXAMPLE, root, ignore=shutil.ignore_patterns("dist", ".dokk"))
    out = build(root).out_dir
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(out)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture(scope="module")
def browser() -> Iterator[object]:
    with playwright.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # browser not downloaded
            pytest.skip(f"chromium not installed: {e}")
        yield b
        b.close()


@pytest.fixture
def page(browser):  # type: ignore[no-untyped-def]
    context = browser.new_context()
    pg = context.new_page()
    pg.problems = []  # console errors and failed requests
    pg.on("console", lambda m: m.type == "error" and pg.problems.append(f"console: {m.text}"))
    pg.on("pageerror", lambda e: pg.problems.append(f"pageerror: {e}"))
    pg.on("requestfailed", lambda r: pg.problems.append(f"failed: {r.url}"))
    pg.on("response", lambda r: r.status >= 400 and pg.problems.append(f"{r.status}: {r.url}"))
    yield pg
    context.close()


def _shot(page, name: str) -> None:  # type: ignore[no-untyped-def]
    if SHOTS:
        page.screenshot(path=str(Path(SHOTS) / f"{name}.png"))


def test_pages_load_without_errors(page, site: str) -> None:  # type: ignore[no-untyped-def]
    for path in (
        "/",
        "/guides/markdown/",
        "/guides/components/",
        "/reference/caf%C3%A9-%C3%BCn%C3%AFcode/",
    ):
        page.goto(site + path)
        page.wait_for_load_state("networkidle")
    assert page.problems == []


def test_mobile_sidebar_toggle(browser, site: str) -> None:  # type: ignore[no-untyped-def]
    context = browser.new_context(viewport={"width": 390, "height": 800})
    page = context.new_page()
    page.goto(site + "/guides/markdown/")
    sidebar = page.locator("#dk-sidebar")
    page.wait_for_function("document.getElementById('dk-sidebar').dataset.sidebarInitialized")
    assert sidebar.get_attribute("aria-hidden") == "true"
    page.get_by_role("button", name="Toggle menu").click()
    page.wait_for_function(
        "document.getElementById('dk-sidebar').getAttribute('aria-hidden') === 'false'"
    )
    _shot(page, "mobile-sidebar-open")
    page.get_by_role("button", name="Toggle menu").click(force=True)
    page.wait_for_function(
        "document.getElementById('dk-sidebar').getAttribute('aria-hidden') === 'true'"
    )
    context.close()


def test_brand_shown_once(page, site: str) -> None:  # type: ignore[no-untyped-def]
    page.goto(site + "/guides/markdown/")
    page.wait_for_function("document.getElementById('dk-sidebar').dataset.sidebarInitialized")
    top = page.locator(".dk-header-title")
    assert not top.is_visible()  # sidebar open: the brand is in the sidebar
    page.get_by_role("button", name="Toggle menu").click()
    page.wait_for_function(
        "document.getElementById('dk-sidebar').getAttribute('aria-hidden') === 'true'"
    )
    assert top.is_visible()  # sidebar collapsed: the brand moves to the top bar


def test_theme_persists_across_reload(page, site: str) -> None:  # type: ignore[no-untyped-def]
    page.goto(site + "/")
    is_dark = "document.documentElement.classList.contains('dark')"
    before = page.evaluate(is_dark)
    page.get_by_role("button", name="Toggle dark mode").click()
    assert page.evaluate(is_dark) is not before
    page.reload()
    assert page.evaluate(is_dark) is not before
    _shot(page, "theme-toggled")


@pytest.mark.skipif(not search_available(), reason="pagefind not installed (search extra)")
def test_search_palette(page, site: str) -> None:  # type: ignore[no-untyped-def]
    page.goto(site + "/")
    _shot(page, "header")
    page.keyboard.press("/")
    dialog = page.locator("#dk-search")
    assert dialog.evaluate("d => d.open")
    page.keyboard.type("zygomorphic")
    first = dialog.get_by_role("menuitem").first
    first.wait_for()
    assert "Nested page" in first.inner_text()
    assert dialog.locator("[role=heading]").inner_text() == "Results"
    assert first.locator("mark").count() >= 1
    _shot(page, "search-results")
    page.keyboard.press("Enter")
    page.wait_for_url("**/guides/advanced/deep/nested/")
    assert page.problems == []


def test_content_does_not_jump_between_pages(browser, site: str) -> None:  # type: ignore[no-untyped-def]
    """Pages with and without an "On this page" column put the content in the same place."""
    for width in (1400, 1000, 390):
        context = browser.new_context(viewport={"width": width, "height": 800})
        page = context.new_page()
        xs = set()
        for path in ("/", "/guides/markdown/", "/guides/advanced/deep/nested/"):
            page.goto(site + path)
            xs.add(round(page.locator("main.dk-main").bounding_box()["x"]))
        assert len(xs) == 1, (width, xs)
        context.close()


def test_synced_tabs_switch_together_and_persist(page, site: str) -> None:  # type: ignore[no-untyped-def]
    page.goto(site + "/guides/components/")
    page.wait_for_function("document.querySelector('.dk-tabs[data-sync]')?.dataset.tabsInitialized")
    selected = (
        "() => [...document.querySelectorAll('.dk-tabs[data-sync] [aria-selected=true][role=tab]')]"
        ".map(t => t.textContent.trim())"
    )
    assert page.evaluate(selected) == ["npm", "npm"]
    page.locator(".dk-tabs[data-sync] [role=tab]", has_text="yarn").first.click()
    assert page.evaluate(selected) == ["yarn", "yarn"]  # both sets switched
    page.reload()
    page.wait_for_function("document.querySelector('.dk-tabs[data-sync]')?.dataset.tabsInitialized")
    page.wait_for_timeout(100)
    assert page.evaluate(selected) == ["yarn", "yarn"]  # remembered
    assert page.problems == []


def test_page_actions_menu_position_and_no_flicker(page, site: str) -> None:  # type: ignore[no-untyped-def]
    page.set_viewport_size({"width": 1400, "height": 800})
    page.goto(site + "/guides/components/")  # has a next page
    page.add_init_script(
        """window.__vis = []; const t0 = performance.now();
        const tick = () => { const el = document.getElementById('dk-page-actions-popover');
          const shown = el && getComputedStyle(el).visibility === 'visible';
          if (shown) window.__vis.push(performance.now() - t0);
          if (performance.now() - t0 < 1000) requestAnimationFrame(tick); };
        requestAnimationFrame(tick);"""
    )
    page.locator('.dk-page-actions a[aria-label^="Next"]').click()
    page.wait_for_timeout(1100)
    assert page.evaluate("window.__vis") == []  # the menu never flashes while a page loads

    page.get_by_role("button", name="More page actions").click()
    page.wait_for_timeout(300)
    trigger = page.locator("#dk-page-actions-trigger").bounding_box()
    menu = page.locator("#dk-page-actions-popover").bounding_box()
    assert 0 <= menu["y"] - (trigger["y"] + trigger["height"]) <= 8  # right under the button
    assert (
        abs((menu["x"] + menu["width"]) - (trigger["x"] + trigger["width"])) <= 2
    )  # right-aligned
    assert page.problems == []
