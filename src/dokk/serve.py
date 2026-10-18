import shutil
import threading
import traceback
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from dokk import DokkError
from dokk.build import build
from dokk.config import CONFIG_FILE, load_config
from dokk.render import base_env, render_template

DEV_DIR = Path(".dokk") / "dev"
VERSION_PATH = "/__dokk/version"


class DevState:
    def __init__(self, root: Path, search: bool = False) -> None:
        self.root = root
        self.search = search
        self.out = root / DEV_DIR
        self.version = 0
        self.error: tuple[str, str] | None = None  # (message, traceback)
        self.lock = threading.Lock()

    def rebuild(self) -> None:
        with self.lock:
            try:
                # Build next to the served folder, then swap, so requests during a rebuild
                # still get the previous site instead of a half-written one.
                fresh, stale = self.out.with_name("dev.next"), self.out.with_name("dev.old")
                build(
                    self.root,
                    drafts=True,
                    dev=True,
                    out_dir=fresh,
                    search=self.search,
                    parallel=True,
                )
                shutil.rmtree(stale, ignore_errors=True)
                if self.out.exists():
                    self.out.rename(stale)
                fresh.rename(self.out)
                shutil.rmtree(stale, ignore_errors=True)
                self.error = None
                print(f"Built (version {self.version + 1})", flush=True)
            except Exception as e:  # show any failure in the browser, keep serving
                message = str(e) if isinstance(e, DokkError) else f"{type(e).__name__}: {e}"
                self.error = (message, traceback.format_exc())
                print(f"error: {message}", flush=True)
            self.version += 1


def error_page(message: str, trace: str) -> bytes:
    # Built-in templates only: the site's own templates may be what is broken.
    return render_template(
        base_env(), "dev_error.html.jinja", message=message, trace=trace
    ).encode()


class DevHandler(SimpleHTTPRequestHandler):
    state: DevState

    def do_GET(self) -> None:
        if self.path == VERSION_PATH:
            self._send(200, str(self.state.version).encode(), "text/plain")
        elif self.state.error:
            self._send(500, error_page(*self.state.error), "text/html; charset=utf-8")
        else:
            super().do_GET()

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        page = self.state.out / "404.html"
        if code == 404 and page.is_file():
            self._send(404, page.read_bytes(), "text/html; charset=utf-8")
        else:
            super().send_error(code, message, explain)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass  # keep the terminal for build output


def watch_paths(root: Path) -> list[Path]:
    """Inputs that trigger a rebuild. They need not exist yet."""
    try:
        content_dir = load_config(root).content_dir
    except DokkError:
        content_dir = root / "docs"
    return [root / CONFIG_FILE, root / "templates", root / "public", content_dir.resolve()]


def is_input(path: Path, inputs: list[Path]) -> bool:
    return any(path == p or path.is_relative_to(p) for p in inputs)


def serve(root: Path, port: int = 8000, search: bool = False) -> None:
    try:
        from watchfiles import watch
    except ImportError:
        raise DokkError("dokk serve needs the serve extra: pip install 'dokk[serve]'") from None

    root = root.resolve()
    load_config(root)  # fail fast on a missing or invalid dokk.toml
    state = DevState(root, search=search)
    state.rebuild()
    handler = type("Handler", (DevHandler,), {"state": state})
    try:
        server = ThreadingHTTPServer(
            ("127.0.0.1", port), partial(handler, directory=str(state.out))
        )
    except OSError as e:
        raise DokkError(f"cannot listen on port {port}: {e.strerror}") from None

    stop = threading.Event()

    def watcher() -> None:
        # ponytail: full rebuild on any change; fine at this scale (PLAN.md phase 4).
        # Watch the root, not the inputs, so folders created later (templates/) are seen.
        inputs = watch_paths(root)

        def accept(_change: object, path: str) -> bool:
            return is_input(Path(path), inputs)

        for changes in watch(root, watch_filter=accept, stop_event=stop):
            print(f"Changed: {', '.join(sorted(Path(p).name for _, p in changes))}", flush=True)
            state.rebuild()
            inputs = watch_paths(root)  # dokk.toml may have moved content_dir

    threading.Thread(target=watcher, daemon=True).start()
    print(f"Serving on http://127.0.0.1:{port}/ (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()
