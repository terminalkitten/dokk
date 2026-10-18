#!/usr/bin/env bash
# Maintainers only: vendor shadcn/ui's color themes (MIT) as JSON. Requires curl and node.
# Usage: scripts/vendor_shadcn_themes.sh [commit]
# Reads apps/v4/registry/themes.ts at a pinned commit and writes src/dokk/data/shadcn-themes.json.
# The TypeScript is converted as text and parsed as JSON, never executed.
# Overwrites in place; update VENDORED.md with the printed commit.
set -euo pipefail

COMMIT="${1:-d2fba50ee5b9113008b5bb908563527b7efd2f27}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/src/dokk/data"
RAW="https://raw.githubusercontent.com/shadcn-ui/ui/$COMMIT"

mkdir -p "$OUT"
curl -fsSL "$RAW/LICENSE.md" > "$OUT/SHADCN-LICENSE"
curl -fsSL "$RAW/apps/v4/registry/themes.ts" | node -e '
  const src = require("fs").readFileSync(0, "utf8");
  const body = src
    .slice(src.indexOf("= [") + 2, src.indexOf("\n] as const") + 2) // the THEMES array
    .replace(/^(\s*)([A-Za-z_][\w-]*):/gm, "$1\"$2\":") // quote bare keys
    .replace(/,(\s*[}\]])/g, "$1"); // drop trailing commas
  const themes = Object.fromEntries(
    JSON.parse(body).map((t) => [t.name, { light: t.cssVars.light, dark: t.cssVars.dark }])
  );
  process.stdout.write(JSON.stringify(themes, null, 1) + "\n");
' > "$OUT/shadcn-themes.json"

echo "Vendored $(node -p "Object.keys(require('$OUT/shadcn-themes.json')).length") shadcn themes from commit $COMMIT"
