"""Maintainers only: vendor basecoat-css into the package. Python stdlib only, no Node.

Usage: python scripts/vendor_basecoat.py [version]

Downloads the npm tarball, checks it against the registry's sha512 integrity, and copies the
needed files straight out of the archive (nothing is extracted to disk). Overwrites files in
place (no deletes); update VENDORED.md with the printed values.
"""

import base64
import hashlib
import json
import sys
import tarfile
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src/dokk/static/vendor/basecoat"
TEMPLATES = ROOT / "src/dokk/templates/basecoat"
STYLES = ("vega", "nova", "maia", "lyra", "mira", "luma", "sera", "rhea")  # standalone packs


def fetch(url: str) -> bytes:
    with urlopen(url, timeout=60) as response:
        return response.read()


def check_integrity(data: bytes, integrity: str) -> None:
    """npm's Subresource Integrity string, e.g. "sha512-<base64>"."""
    algorithm, _, expected = integrity.partition("-")
    actual = base64.b64encode(hashlib.new(algorithm, data).digest()).decode()
    if actual != expected:
        raise SystemExit(f"integrity mismatch: expected {integrity}, got {algorithm}-{actual}")


def destinations(names: list[str]) -> dict[str, Path]:
    """Archive member -> where it goes. Every npm tarball member starts with package/."""
    wanted = {f"package/dist/basecoat-{s}.cdn.min.css": STATIC for s in STYLES}
    wanted["package/dist/js/all.min.js"] = STATIC
    out = {name: folder / Path(name).name for name, folder in wanted.items()}
    out["package/LICENSE.md"] = STATIC / "LICENSE"
    for name in names:
        parent, _, file = name.rpartition("/")
        if parent == "package/templates/jinja" and file.endswith(".html.jinja"):
            out[name] = TEMPLATES / file
    return out


def main(version: str = "1.0.2") -> None:
    meta = json.loads(fetch(f"https://registry.npmjs.org/basecoat-css/{version}"))
    tarball, integrity = meta["dist"]["tarball"], meta["dist"]["integrity"]
    data = fetch(tarball)
    check_integrity(data, integrity)

    with tarfile.open(fileobj=BytesIO(data), mode="r:gz") as archive:
        targets = destinations(archive.getnames())
        for name, dest in targets.items():
            member = archive.extractfile(name)  # KeyError if the package layout changed
            if member is None:
                raise SystemExit(f"{name} is not a file")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(member.read())

    print(f"Vendored basecoat-css@{version} ({len(targets)} files)")
    print(f"Tarball: {tarball}")
    print(f"Integrity: {integrity}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
