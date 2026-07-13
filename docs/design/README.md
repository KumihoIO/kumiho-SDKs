# Kumiho Brain — design north-star

`kumiho-brain-northstar.html` is the interactive design north-star for the
**Kumiho Brain** dashboard (see [issue #57](https://github.com/KumihoIO/kumiho-SDKs/issues/57)).

## How to view

It is a **single self-contained file** — no build step, no external requests
(all CSS/JS/WebGL inlined). Just open it in a browser:

```bash
# macOS
open   docs/design/kumiho-brain-northstar.html
# Linux
xdg-open docs/design/kumiho-brain-northstar.html
# Windows
start  docs/design/kumiho-brain-northstar.html
```

(Opening the file locally is required — GitHub serves raw `.html` as text, so
the raw link won't render.)

## What it demonstrates (target look & feel — build toward this)

- **Procedural nebula background glow** — WebGL fbm-noise gas filaments, cool-blue
  core + warm-orange outer, slow churn, bright center; deep-space black.
- **Memory graph as glowing nodes** — blue = conversation memory, amber =
  code / decision; a shimmering k-nearest **interlink web**; slow auto-orbit,
  glow pulse, drift, and a periodic "new memory" bloom.
- **HUD "terminal" shell** — muted, mono, hairline frame; aligned to kumiho.io's
  dark/minimal identity (not a marketing page).
- **Interactive & functional** — live **search** (`/` to focus), **filters**
  (kind / source client), **top hubs** (most-linked), and **click-to-inspect**
  (any node → its content, kind, source, typed interlinks).

## Notes for implementers

- Sample data is illustrative. The real build streams the **live graph via the
  Rust `kumiho` SDK** (`rust/`) — snapshot + WebSocket — per the architecture in
  #57. Evolve this file's pure-WebGL2 render into the **M2 render core**.
- Pure WebGL2 (`gl.POINTS` additive glow + `gl.LINES` + a fullscreen nebula
  pass). Transform-feedback-friendly motion; LOD/clustering at scale.
