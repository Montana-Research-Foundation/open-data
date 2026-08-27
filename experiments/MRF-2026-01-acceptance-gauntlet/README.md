<p align="center">
  <a href="https://montanaresearch.org">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/mrf-lockup-dark.svg">
      <img src="assets/mrf-lockup-light.svg" alt="Montana Research Foundation" width="340">
    </picture>
  </a>
</p>

<p align="center">
  <img alt="preprint" src="https://img.shields.io/badge/preprint-MRF--2026--01-9184CF"> <img alt="version" src="https://img.shields.io/badge/version-v1-5A5A66"> <img alt="license" src="https://img.shields.io/badge/license-CC%20BY%204.0-5A5A66"> <a href="https://doi.org/10.5281/zenodo.22126529"><img alt="DOI" src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22126529-9184CF"></a> <img alt="rollouts" src="https://img.shields.io/badge/rollouts-120-B3A8E6">
</p>

---

# MRF-2026-01 data bundle

**ATLAS: Adversarial, Traceable, Latent-Criterion, Auditable, and Seed-Calibrated Task Acceptance**
Montana Research Foundation preprint MRF-2026-01.

This is the data behind the paper: the aggregate outcome of every
rollout, and a self-contained script that recomputes the headline from
it. The task families, the raw agent transcripts, and the held-out
grading data are withheld under contamination control (`WITHHELD.md`).
The paper's LaTeX source and its figure and table generators live with
the preprint, not here; this bundle is the data and its verifier only.

## What is here

- `records/` — one `.jsonl` per experimental cell, one line per rollout,
  aggregate fields only: seed, arm (`track`), configuration, reward
  (`score`), `passed`, token counts (including the reasoning-token count
  lifted out of the transcript), turns, and cost where the scaffold meters
  it. No transcript, task text, induced rule, or canary.
- `verify.py` — recomputes the per-cell pass rates and Wilson intervals
  directly from `records/`, with no other file and no task content.
- `WITHHELD.md`, `LICENSE` (CC BY 4.0), `MANIFEST.sha256`.

## Verify

    python3 verify.py

The printed pass rates, intervals, match the paper. `verify.py`
reads only `records/`.

## Cells in this bundle

  - rule-induction-cli
  - rule-induction-gpt
  - protocol-induction-cli
  - protocol-induction-gpt
  - format-induction-cli
  - format-induction-gpt

## Citation

Cite the preprint MRF-2026-01 and this data bundle by its DOI (minted on
release; see the preprint's front matter).
