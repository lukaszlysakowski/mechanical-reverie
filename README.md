# Mechanical Reverie

**A generative art engine shaped by art history, one day at a time.**

→ **[View the timeline](https://lukaszlysakowski.github.io/mechanical-reverie/)**

---

Each day, the system reads [@Noahbolanowski](https://x.com/Noahbolanowski)'s tweets about art and technology history — surfacing forgotten moments where computation first met artistic practice — and generates a new artwork from what it hears.

The piece is not an illustration of the tweets. It is a translation: the day's dominant themes, the images' color temperature, the emotional register of the language — all encoded into a genome of ~25 parameters that governs palette, pixel density, flow character, geometric weight, organic drift, and mechanical presence. Twelve candidates render; the best is selected by an aesthetic fitness function, with occasional curatorial overrides when theme and fitness disagree.

The winning genome enters an ancestry archive and breeds future generations. Over time, the system develops aesthetic preferences — recurring palette combinations, structural signatures, depth formulas — that evolve from the accumulated pressure of past selections.

---

## How the timeline reads

- **Each card** is one day's winner
- **The score badge** (1–10) is the curator's aesthetic judgment
- **The reason text** is an algorithmic catalogue note — what the system heard, and why it made the choices it made
- **Dashed lines** between cards show lineage: when a genome influenced a later generation
- **★** marks Hall of Fame entries that spawned 3+ descendants
- **†** marks extinct genomes with no descendants
- **Gap markers** (e.g. `2d`) show days where no tweets were posted

---

## Updating

The `publish.sh` script copies the latest artwork and genome data from the working directory and pushes to GitHub Pages:

```bash
cd /path/to/mechanical-reverie-public
./publish.sh "Day 45 — Future Mural"
```

---

## Technical stack

- Canvas 2D rendering (vanilla JS, no dependencies)
- Six rendering primitives: pixel blobs, flow fields, gear/starburst mechanics, plotter hatching, organic forms, geometric shapes
- 25+ genome parameters controlling every visual dimension
- Ancestry evolution: active, Hall of Fame (★), and extinct (†) lineages
- Tweet theme analysis → genome bias → 12 candidates → fitness selection

---

*Started March 29, 2026. Updated nightly.*
