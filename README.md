<p align="center">
  <a href="https://montanaresearch.org">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/mrf-lockup-dark.svg">
      <img src="assets/mrf-lockup-light.svg" alt="Montana Research Foundation" width="340">
    </picture>
  </a>
</p>

<p align="center">
  <img alt="license" src="https://img.shields.io/badge/license-CC%20BY%204.0-5A5A66"> <img alt="bundles" src="https://img.shields.io/badge/bundles-3-9184CF"> <img alt="rollouts" src="https://img.shields.io/badge/rollouts-760-B3A8E6">
</p>

---

# Reproducibility data

One directory per preprint, under `experiments/`. Each is the data behind
its paper: the aggregate outcome of every rollout, and a
self-contained `verify.py` that recomputes the headline from it. The task
families, the raw agent transcripts, and the held-out grading data are
withheld under contamination control (each bundle's `WITHHELD.md`).

| bundle | measures | rollouts |
|---|---|---|
| [`MRF-2026-01-acceptance-gauntlet`](experiments/MRF-2026-01-acceptance-gauntlet/) | task acceptance and seed calibration | 120 |
| [`MRF-2026-02-held-out-confidence`](experiments/MRF-2026-02-held-out-confidence/) | agent self-knowledge under a held-out criterion | 240 |
| [`MRF-2026-03-track-label`](experiments/MRF-2026-03-track-label/) | an ability label raises the effort of an agent | 400 |

## What each bundle contains

- `records/` — one `.jsonl` per experimental cell, one line per rollout,
  aggregate fields only (seed, arm, configuration, score, pass, token
  counts, turns). No transcript, task text, induced rule, or canary.
- `dataset.json` — the computed aggregate the paper reports (where the
  paper has one).
- `verify.py` — recomputes the per-cell pass rates and intervals from
  `records/` alone, with no task content.
- `CITATION.cff` — the experiment's citation, carrying its own DOI once
  minted.
- `zenodo.json` — Zenodo deposition metadata for minting that DOI.
- `README.md`, `WITHHELD.md`, `LICENSE` (CC BY 4.0), `MANIFEST.sha256`.

The paper's LaTeX source and its figure and table scripts live with the
preprint, not here; these bundles are the data and its verifier.

## Verify

    cd <bundle> && python3 verify.py

The printed rates and intervals match the paper.

## Release

Each experiment is deposited to Zenodo as its own record, so it carries
its own DOI. On release, the DOI is written into that experiment's
`CITATION.cff` and into the matching preprint's front matter
(`\mrfdoi`). Cite each experiment from its own `CITATION.cff`; there is
no repository-level DOI.
