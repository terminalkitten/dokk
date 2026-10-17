#!/usr/bin/env bash
# Maintainers only: vendor basecoat-css into the package. Requires npm.
# Usage: scripts/vendor_basecoat.sh [version]
set -euo pipefail

VERSION="${1:-1.0.2}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATIC="$ROOT/src/dokk/static/vendor/basecoat"
TEMPLATES="$ROOT/src/dokk/templates/basecoat"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

(cd "$TMP" && npm pack --silent "basecoat-css@$VERSION" >/dev/null)
tar -xzf "$TMP"/basecoat-css-*.tgz -C "$TMP"
PKG="$TMP/package"

rm -rf "$STATIC" "$TEMPLATES"
mkdir -p "$STATIC" "$TEMPLATES"
cp "$PKG/dist/basecoat.cdn.min.css" "$PKG/dist/js/all.min.js" "$STATIC/"
cp "$PKG/LICENSE.md" "$STATIC/LICENSE"
cp "$PKG"/templates/jinja/*.html.jinja "$TEMPLATES/"

INTEGRITY="$(npm view "basecoat-css@$VERSION" dist.integrity)"
{
  echo "# Vendored files"
  echo
  echo "## Basecoat"
  echo
  echo "- Package: \`basecoat-css@$VERSION\` (MIT, see \`src/dokk/static/vendor/basecoat/LICENSE\`)"
  echo "- Tarball: https://registry.npmjs.org/basecoat-css/-/basecoat-css-$VERSION.tgz"
  echo "- Integrity: \`$INTEGRITY\`"
  echo "- Updated with: \`scripts/vendor_basecoat.sh $VERSION\`"
  echo
  echo "| Source in package | Destination |"
  echo "|---|---|"
  echo "| \`dist/basecoat.cdn.min.css\` | \`src/dokk/static/vendor/basecoat/\` |"
  echo "| \`dist/js/all.min.js\` | \`src/dokk/static/vendor/basecoat/\` |"
  echo "| \`LICENSE.md\` (as \`LICENSE\`) | \`src/dokk/static/vendor/basecoat/\` |"
  echo "| \`templates/jinja/*.html.jinja\` | \`src/dokk/templates/basecoat/\` |"
} > "$ROOT/VENDORED.md"

echo "Vendored basecoat-css@$VERSION"
