#!/bin/bash
# publish.sh — Copy latest art and genome data from working directory, then push to GitHub Pages
#
# Usage: ./publish.sh "Day 46 — Title Here"
#        ./publish.sh  (uses auto-generated commit message from latest genome entry)

set -e

SRC="/Users/lukasz/claude/mechanical-reverie"
DST="$(dirname "$0")"
ART_SRC="$SRC/generative-art-output/art"
ART_DST="$DST/art"

echo "→ Syncing selected-genomes.json..."
cp "$SRC/selected-genomes.json" "$DST/selected-genomes.json"

echo "→ Syncing site files (pages + data)..."
# These live only in the working dir and used to require manual copying — the source of
# stale-site drift. Sync them every publish so the deployed site never lags the working copy.
for f in index.html timeline.html atlas.html concepts.html csuri.html generative-art-generator.html concepts.json elites-map.json; do
  if [ -f "$SRC/$f" ]; then
    if ! cmp -s "$SRC/$f" "$DST/$f"; then
      cp "$SRC/$f" "$DST/$f"
      echo "  ~ $f (updated)"
    fi
  fi
done

echo "→ Syncing art files..."
# Copy any referenced PNG that isn't already in the public art dir
python3 - <<'PYEOF'
import json, shutil, os, sys

src = os.environ.get('ART_SRC', '/Users/lukasz/claude/mechanical-reverie/generative-art-output/art')
dst = os.environ.get('ART_DST', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'art'))

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'selected-genomes.json')) as f:
    genomes = json.load(f)

copied = 0
for g in genomes:
    fn = g.get('filename', '')
    if not fn:
        continue
    src_path = os.path.join(src, fn)
    dst_path = os.path.join(dst, fn)
    if os.path.exists(src_path) and not os.path.exists(dst_path):
        shutil.copy2(src_path, dst_path)
        print(f'  + {fn}')
        copied += 1

if copied == 0:
    print('  (no new files)')
else:
    print(f'  Copied {copied} new file(s)')
PYEOF

# Build commit message
if [ -n "$1" ]; then
  MSG="$1"
else
  # Auto-generate from the last genome entry
  MSG=$(python3 -c "
import json
with open('selected-genomes.json') as f:
    g = json.load(f)
last = g[-1]
date = last.get('date', '?')
name = last.get('name', last.get('title', last.get('filename', '?')))
print(f'Update {date} — {name}')
")
fi

echo "→ Committing: $MSG"
cd "$DST"
git add .
git diff --cached --quiet && echo "  (nothing to commit)" && exit 0
git commit -m "$MSG"

echo "→ Pushing to GitHub..."
git push origin main

echo ""
echo "✓ Published: https://lukaszlysakowski.github.io/mechanical-reverie/"
