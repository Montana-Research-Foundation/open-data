<p align="center">
  <a href="https://montanaresearch.org">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/mrf-lockup-dark.svg">
      <img src="assets/mrf-lockup-light.svg" alt="Montana Research Foundation" width="340">
    </picture>
  </a>
</p>

<p align="center">
  <img alt="preprint" src="https://img.shields.io/badge/preprint-MRF--2026--02-9184CF"> <img alt="version" src="https://img.shields.io/badge/version-1.0.1-5A5A66"> <img alt="license" src="https://img.shields.io/badge/license-CC%20BY%204.0-5A5A66"> <a href="https://doi.org/10.5281/zenodo.22126530"><img alt="DOI" src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22126530-9184CF"></a> <img alt="rollouts" src="https://img.shields.io/badge/rollouts-240-B3A8E6">
</p>

---

# MRF-2026-02 data bundle

**Measuring Agent Self-Knowledge Under a Criterion Held Out of the Environment**
Montana Research Foundation preprint MRF-2026-02.

This is the data behind the paper: the aggregate outcome of every
rollout in the reported panel, and a self-contained script that
recomputes the headline from it. The task families, the raw agent
transcripts, and the held-out grading data are withheld under
contamination control (`WITHHELD.md`).
The paper's LaTeX source and its figure and table generators live with
the preprint, not here; this bundle is the data and its verifier only.

## What is here

- `records/` — one `.jsonl` per experimental cell, one line per rollout,
  aggregate fields only. The fields present in this bundle's records:
  `agent_wall_s`*, `cli_cost_usd`*, `configuration`, `driver`*, `family`, `harness_version`*, `input_tokens`, `is_error`*, `metrics`, `model_id`, `num_turns`, `output_tokens`, `passed`, `score`, `seed`, `stop`*.
  Fields marked * are absent from some records; where a record lacks a
  field, that quantity was not captured for that rollout.
  The pass rule is: `passed` iff `score` >= 0.5 (the reward the grader
  returned); `verify.py` re-derives the flag on every record. No
  transcript, task text, induced rule, or canary.
- `dataset.json` — the computed aggregate the paper reports (cells, effect sizes, intervals), for reference and cross-checking.
- `verify.py` — recomputes the per-cell pass rates and Wilson intervals
  and, for every cell, the mean declared confidence and the overconfidence
  gap (mean declaration minus pass rate, both over the declaring
  rollouts) directly from `records/`, with no other file and no task
  content, and re-derives every `passed` flag from `score`.
- `WITHHELD.md`, `LICENSE` (CC BY 4.0), `MANIFEST.sha256`.

## Verify

    python3 verify.py

The printed pass rates, intervals, and overconfidence gaps match the paper. `verify.py`
reads only `records/`.

## Notes on the records

- One rollout (`rule-induction-confidence-cli`, seed 15) errored in transport (`is_error`) and recorded no declaration. It counts as a failure in that cell's pass rate and is absent from the declaration mean, which is why the declared n there is 19 where the paper says so.
- In `dataset.json`, the per-cell `s1` statistics and the six `ablation_gap_reduction` deltas recompute from `records/` alone (`verify.py` prints the ingredients). The `paired_rule` block compares against base-family control rollouts that are not part of this release, and `val_per_seed` derives from the withheld validation data; those blocks are reference values from the paper's committed audit, not recomputable here.
- The per-seed localization detail behind the `s2_rule` aggregates names the withheld family's features, clauses, and parameters, and is redacted from the released `dataset.json` under contamination control; the aggregate hit rates and baselines the paper quotes are retained.

## Cells in this bundle

  - rule-induction-confidence-cli
  - rule-induction-confidence-gpt
  - rule-induction-confidence-val-cli
  - rule-induction-confidence-val-gpt
  - protocol-induction-confidence-cli
  - protocol-induction-confidence-gpt
  - protocol-induction-confidence-val-cli
  - protocol-induction-confidence-val-gpt
  - format-induction-confidence-cli
  - format-induction-confidence-gpt
  - format-induction-confidence-val-cli
  - format-induction-confidence-val-gpt

## Citation

Cite the preprint MRF-2026-02 and this data bundle by the DOI in
`CITATION.cff` (the concept DOI, which resolves to the latest deposited
version of this bundle).
