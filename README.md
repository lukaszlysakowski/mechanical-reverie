# Mechanical Reverie

**A self-learning generative art engine that reads art history and answers in its own language — one artwork a day.**

Each day the system reads [@Noahbolanowski](https://x.com/Noahbolanowski)'s posts on the history of computer art — the moments computation first met artistic practice — and renders a new piece in response. Nothing here is hand-drawn: the work is the *engine*. Following Harold Cohen and AARON, when the engine can't do something a source demands, the program is changed, never the individual picture — so its vocabulary grows over time (see **[Lineage](LINEAGE.md)**). Ninety-plus days in, the archive has begun to develop a signature of its own.

→ **[Open the project](https://lukaszlysakowski.github.io/mechanical-reverie/)** · start with the **[Concepts screen](https://lukaszlysakowski.github.io/mechanical-reverie/concepts.html)** to read the archive as an argument.

**Four ways to read the archive:**
- **[Timeline](https://lukaszlysakowski.github.io/mechanical-reverie/timeline.html)** — chronology: every day's winner, in order, with lineage.
- **[The Atlas](https://lukaszlysakowski.github.io/mechanical-reverie/atlas.html)** — capability: a MAP-Elites survey of the engine's possibility space, and the frontier it has never rendered.
- **[Concepts](https://lukaszlysakowski.github.io/mechanical-reverie/concepts.html)** — argument: curated rooms tracing what the archive has been thinking about (Bell Labs, Women Pioneers, The Sonic Dimension, artist studies, and more).
- **[Csuri Lineage](https://lukaszlysakowski.github.io/mechanical-reverie/csuri.html)** — a deep single-artist study.

Recent chapters in the engine's own evolution: a **disorder dial** (Molnár's 1% / Nees's *Schotter* — order collapsing along a spatial gradient), **canonical seeds** (each artwork is a reproducible *score*, not just a print), and **a sonic dimension** (every genome already encodes a chord — press ◐ Sound in the generator to hear it).

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
