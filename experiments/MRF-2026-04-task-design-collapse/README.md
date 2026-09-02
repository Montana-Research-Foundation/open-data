<p align="center">
  <a href="https://montanaresearch.org">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/mrf-lockup-dark.svg">
      <img src="assets/mrf-lockup-light.svg" alt="Montana Research Foundation" width="340">
    </picture>
  </a>
</p>

<p align="center">
  <img alt="preprint" src="https://img.shields.io/badge/preprint-MRF--2026--04-9184CF"> <img alt="version" src="https://img.shields.io/badge/version-v1-5A5A66"> <img alt="license" src="https://img.shields.io/badge/license-CC%20BY%204.0-5A5A66"> <a href="https://doi.org/10.5281/zenodo.22250740"><img alt="DOI" src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22250740-9184CF"></a> <img alt="rollouts" src="https://img.shields.io/badge/rollouts-2-B3A8E6">
</p>

---

# MRF-2026-04 data bundle

**Fair and cheap: eight task designs for frontier evaluation in quantitative finance**
Montana Research Foundation preprint MRF-2026-04.

This is the data behind the paper. The paper screens 8 task
designs against a fixed protocol and reports that every one of them fell,
most of them before any model ran, so the bundle is shaped by that
result: one probed cell of 2 rollouts, and the consolidated
gate-0 dataset the manuscript is written from. The task families, the
screening spike code, the raw agent transcripts, and the held-out grading
data are withheld under contamination control (`WITHHELD.md`). The
paper's LaTeX source and its figure and table generators live with the
preprint, not here.

## What is here

- `records/` — the one probed cell, one line per rollout, aggregate
  fields only: the reward the verifier returned, `passed`, whether the
  trial errored and with which exception, token counts, metered cost, and
  the agent and verifier wall clocks. No transcript, task text, submitted
  method, or canary.
- `dataset.json` — the consolidated gate-0 dataset. Every value carries a
  `source` and a `method`: `parsed` from a committed file, `derived` from
  one by a stated rule, `transcribed` from a numbered line of a committed
  report, or `maintained` in the census. This is the file the manuscript's
  macros, tables, and figures are generated from.
- `verify.py` — recomputes the probe's pass rate and Wilson interval from
  `records/`, recounts the designs by disposition and by what retired
  them, checks those recounts against the scalars the manuscript quotes,
  and reports the provenance mix. It reads only this directory.
- `WITHHELD.md`, `LICENSE` (CC BY 4.0), `MANIFEST.sha256`.

## Verify

    python3 verify.py

Every recount printed matches the paper.

## Why there is one cell and not a grid

Five designs were retired at gate 0 on measurements that cost laptop
compute and no model spend, two on an argument from shared structure with
a measured one, and one by the probe whose rollouts are in `records/`.
Seven of the eight therefore never ran against a model. The absence of a
difficulty distribution is the paper's finding rather than an omission
from this bundle, and `verify.py` recounts those dispositions from
`dataset.json` on every run.

## Citation

Cite the preprint MRF-2026-04 and this data bundle by its DOI (minted on
release; see the preprint's front matter).
