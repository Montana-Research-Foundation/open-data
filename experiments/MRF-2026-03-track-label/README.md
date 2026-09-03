<p align="center">
  <a href="https://montanaresearch.org">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/mrf-lockup-dark.svg">
      <img src="assets/mrf-lockup-light.svg" alt="Montana Research Foundation" width="340">
    </picture>
  </a>
</p>

<p align="center">
  <img alt="preprint" src="https://img.shields.io/badge/preprint-MRF--2026--03-9184CF"> <img alt="version" src="https://img.shields.io/badge/version-1.0.1-5A5A66"> <img alt="license" src="https://img.shields.io/badge/license-CC%20BY%204.0-5A5A66"> <a href="https://doi.org/10.5281/zenodo.22126532"><img alt="DOI" src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22126532-9184CF"></a> <img alt="rollouts" src="https://img.shields.io/badge/rollouts-400-B3A8E6">
</p>

---

# MRF-2026-03 data bundle

**An Ability Label Raises the Effort of an Agent**
Montana Research Foundation preprint MRF-2026-03.

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
  `agent_wall_s`*, `cli_cost_usd`*, `configuration`, `driver`*, `family`, `harness_version`*, `input_tokens`, `is_error`*, `metrics`, `model_id`, `num_turns`, `output_tokens`, `passed`, `score`, `seed`, `stop`*, `thinking_tokens`*, `track`.
  Fields marked * are absent from some records; where a record lacks a
  field, that quantity was not captured for that rollout.
  The pass rule is: `passed` iff `score` >= 0.5 (the reward the grader
  returned); `verify.py` re-derives the flag on every record. No
  transcript, task text, induced rule, or canary.
- `dataset.json` — the computed aggregate the paper reports (cells, effect sizes, intervals), for reference and cross-checking.
- `verify.py` — recomputes the per-cell pass rates and Wilson intervals
  and the confirmatory reasoning-token effect (paired $d$ and exact
  signed-rank $p$) directly from `records/`, with no other file and no
  task content, and re-derives every `passed` flag from `score`.
- `WITHHELD.md`, `LICENSE` (CC BY 4.0), `MANIFEST.sha256`.

## Verify

    python3 verify.py

The printed pass rates, intervals, and effect sizes match the paper. `verify.py`
reads only `records/`.

## Notes on the records

- The stage-2 GPT-5.6 Sol cells carry no `thinking_tokens`: the runner did not capture the reasoning-token field in those runs, as the paper reports. The stage-3 to stage-5 cells do.
- In `dataset.json`, `cost_usd` for the stage-2 GPT cells is the string `token-bound-pending`: no billed figure exists for those cells and no bound was carried into the aggregate. `gpt_effort_cost.usd_bound` covers the 140 stage-3 to stage-5 GPT rollouts only.
- `dataset.json`'s `source` field names the audit file in the internal research repository this aggregate was computed from, with its sha256. That repository is not public; nothing in this bundle depends on resolving the path.

## Cells in this bundle

  - protocol-induction-track-remedial-cli
  - protocol-induction-track-remedial-gpt
  - protocol-induction-track-advanced-cli
  - protocol-induction-track-advanced-gpt
  - protocol-induction-track-standard-cli
  - protocol-induction-track-standard-gpt
  - protocol-induction-track3-advanced-cli
  - protocol-induction-track3-advanced-gpt
  - protocol-induction-track3-standard-cli
  - protocol-induction-track3-standard-gpt
  - protocol-induction-track4-remedial-individual-cli
  - protocol-induction-track4-remedial-individual-gpt
  - protocol-induction-track4-standard-individual-cli
  - protocol-induction-track4-standard-individual-gpt
  - protocol-induction-track5-remedial-individual-cli
  - protocol-induction-track5-remedial-individual-gpt
  - protocol-induction-track5-standard-individual-cli
  - protocol-induction-track5-standard-individual-gpt

## Citation

Cite the preprint MRF-2026-03 and this data bundle by the DOI in
`CITATION.cff` (the concept DOI, which resolves to the latest deposited
version of this bundle).
