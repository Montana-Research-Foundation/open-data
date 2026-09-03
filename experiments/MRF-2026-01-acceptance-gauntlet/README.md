<p align="center">
  <a href="https://montanaresearch.org">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/mrf-lockup-dark.svg">
      <img src="assets/mrf-lockup-light.svg" alt="Montana Research Foundation" width="340">
    </picture>
  </a>
</p>

<p align="center">
  <img alt="preprint" src="https://img.shields.io/badge/preprint-MRF--2026--01-9184CF"> <img alt="version" src="https://img.shields.io/badge/version-1.0.1-5A5A66"> <img alt="license" src="https://img.shields.io/badge/license-CC%20BY%204.0-5A5A66"> <a href="https://doi.org/10.5281/zenodo.22126528"><img alt="DOI" src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22126528-9184CF"></a> <img alt="rollouts" src="https://img.shields.io/badge/rollouts-120-B3A8E6">
</p>

---

# MRF-2026-01 data bundle

**ATLAS: Adversarial, Traceable, Latent-Criterion, Auditable, and Seed-Calibrated Task Acceptance**
Montana Research Foundation preprint MRF-2026-01.

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
- `verify.py` — recomputes the per-cell pass rates and Wilson intervals
  directly from `records/`, with no other file and no task content, and
  re-derives every `passed` flag from `score`.
- `WITHHELD.md`, `LICENSE` (CC BY 4.0), `MANIFEST.sha256`.

## Verify

    python3 verify.py

The printed pass rates and intervals match the paper. `verify.py`
reads only `records/`.

## Notes on the records

- The records are the rollouts of the panel the paper reports. Attempts the paper excludes under its outcome-independent fault rule (provider-side terminations) are retained in the internal run records and are not part of this release.
- Seeds 0-4 of `rule-induction-cli` were graded under the paper's pre-segmentation rubric and carry a smaller `metrics` map than the other records; the manuscript's methods section describes the rubric change.
- `agent_wall_s` is the agent-execution phase as the scaffold metered it. The paper's committed panel also carries a wall clock with a wider phase boundary, larger by one to a few seconds per rollout; only `agent_wall_s` ships here.

## Cells in this bundle

  - rule-induction-cli
  - rule-induction-gpt
  - protocol-induction-cli
  - protocol-induction-gpt
  - format-induction-cli
  - format-induction-gpt

## Citation

Cite the preprint MRF-2026-01 and this data bundle by the DOI in
`CITATION.cff` (the concept DOI, which resolves to the latest deposited
version of this bundle).
