---
name: New experiment release
about: Prepare and release a new experiment's reproducibility data
title: "release: <MRF-YYYY-NN> <slug>"
labels: [release]
---

## Experiment

- Preprint number:
- Title:
- Directory: `experiments/<MRF-YYYY-NN>-<slug>/`

## Release checklist

- [ ] Bundle generated (records, verify.py, dataset.json where applicable)
- [ ] `CITATION.cff` and `zenodo.json` present and correct
- [ ] `python .github/scripts/validate_release.py` passes
- [ ] Deposited to Zenodo; DOI minted
- [ ] DOI written into `CITATION.cff`, `zenodo.json`, and the preprint `\mrfdoi`

Create the working branch from this issue.
