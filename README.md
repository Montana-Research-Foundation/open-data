<p align="center">
  <a href="https://montanaresearch.org">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/mrf-lockup-dark.svg">
      <img src="assets/mrf-lockup-light.svg" alt="Montana Research Foundation" width="340">
    </picture>
  </a>
</p>

<p align="center">
  <img alt="license" src="https://img.shields.io/badge/license-CC%20BY%204.0-5A5A66"> <img alt="bundles" src="https://img.shields.io/badge/bundles-4-9184CF"> <img alt="rollouts" src="https://img.shields.io/badge/rollouts-762-B3A8E6">
</p>

---

# Reproducibility data

One directory per preprint, under `experiments/`. Each is the data behind
its paper: the aggregate outcome of every rollout in the reported
panel, and a self-contained `verify.py` that recomputes the headline
statistics from it. The task
families, the raw agent transcripts, and the held-out grading data are
withheld under contamination control (each bundle's `WITHHELD.md`).

| bundle | measures | rollouts |
|---|---|---|
| [`MRF-2026-01-acceptance-gauntlet`](experiments/MRF-2026-01-acceptance-gauntlet/) | task acceptance and seed calibration | 120 |
| [`MRF-2026-02-held-out-confidence`](experiments/MRF-2026-02-held-out-confidence/) | agent self-knowledge under a held-out criterion | 240 |
| [`MRF-2026-03-track-label`](experiments/MRF-2026-03-track-label/) | an ability label raises the effort of an agent | 400 |
| [`MRF-2026-04-task-design-collapse`](experiments/MRF-2026-04-task-design-collapse/) | eight quantitative-finance task designs, screened and retired | 2 |

## What each bundle contains

- `records/` — one `.jsonl` per experimental cell, one line per rollout,
  aggregate fields only; each bundle's `README.md` lists the exact
  fields its records carry. No transcript, task text, induced rule, or
  canary.
- `dataset.json` — the computed aggregate the paper reports (where the
  paper has one).
- `verify.py` — recomputes that bundle's per-cell statistics from
  `records/` alone, with no task content, and re-derives every `passed`
  flag from `score` (pass rule: `score` >= 0.5).
- `CITATION.cff` — the experiment's citation, carrying its concept DOI
  (which resolves to the latest deposited version).
- `zenodo.json` — Zenodo deposition metadata for that experiment.
- `README.md`, `WITHHELD.md`, `LICENSE` (CC BY 4.0), `MANIFEST.sha256`.

The paper's LaTeX source and its figure and table scripts live with the
preprint, not here; these bundles are the data and its verifier.

## Verify

    cd <bundle> && python3 verify.py

The printed rates and intervals match the paper.

## Release

Each experiment is deposited to Zenodo as its own record, so it carries
its own DOI. The `CITATION.cff` carries the experiment's concept DOI,
which resolves to the latest deposited version; each deposited version
additionally receives its own version DOI from Zenodo. A release of a
bundle version is tagged `<experiment>-v<version>` on the merge commit,
and the deposit's `isIdenticalTo` names that tag. Cite each experiment
from its own `CITATION.cff`; there is no repository-level DOI.
