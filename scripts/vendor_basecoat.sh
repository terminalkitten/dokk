#!/usr/bin/env bash
# Maintainers only: vendor basecoat-css into the package. Requires npm.
# Usage: scripts/vendor_basecoat.sh [version]
# Overwrites files in place (no deletes); update VENDORED.md with the printed values.
set -euo pipefail

VERSION="${1:-1.0.2}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATIC="$ROOT/src/dokk/static/vendor/basecoat"
TEMPLATES="$ROOT/src/dokk/templates/basecoat"
TMP="$(mktemp -d)"  # left for the OS to clean up

(cd "$TMP" && npm pack --silent "basecoat-css@$VERSION" >/dev/null)
tar -xzf "$TMP"/basecoat-css-*.tgz -C "$TMP"
PKG="$TMP/package"

mkdir -p "$STATIC" "$TEMPLATES"
for STYLE in vega nova maia lyra mira luma sera rhea; do  # standalone style packs
  cp "$PKG/dist/basecoat-$STYLE.cdn.min.css" "$STATIC/"
done
cp "$PKG/dist/js/all.min.js" "$STATIC/"
cp "$PKG/LICENSE.md" "$STATIC/LICENSE"
cp "$PKG"/templates/jinja/*.html.jinja "$TEMPLATES/"

echo "Vendored basecoat-css@$VERSION"
echo "Integrity: $(npm view "basecoat-css@$VERSION" dist.integrity)"
