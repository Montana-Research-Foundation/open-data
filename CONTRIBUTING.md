# Contributing

This repository holds the reproducibility data behind the Montana Research
Foundation preprints. Changes follow one flow, and validation runs on every
pull request.

## The flow: issue -> branch -> pull request -> main

1. **Open an issue** using a template (New experiment release, or Data
   correction). Every change starts from an issue.
2. **Create the branch from the issue** — on the issue page, Development ->
   Create a branch. This links the branch to the issue; the branch name is
   `<issue-number>-<slug>`.
3. **Make the change** and run the validator locally:

       pip install pyyaml
       python .github/scripts/validate_release.py

4. **Open a pull request** into `main` and reference the issue in the body
   (`Closes #<n>`). The `pr-policy` check fails a PR that references no issue.
5. **Pass CI and review.** The `datasets` check must be green and the code
   owner (see `.github/CODEOWNERS`) reviews. Then merge to `main`.

Do not push directly to `main`, and do not force-push it.

## Commits

- Commits are **GPG-signed**. The signing identity for this repository is
  `Francieli Carra <fran.carra@montanalabs.ai>`.
- Right now `francielicarra` is the only user with push access.

## What CI validates (`datasets`)

For every experiment under `experiments/`:

- required files are present;
- `MANIFEST.sha256` matches every file and covers every file (integrity);
- `verify.py` runs to completion;
- `CITATION.cff` and `zenodo.json` are valid and complete;
- the README rollout count matches the records;
- no local paths or private-key blocks leak into shipped files.

## Branch protection

Apply the ruleset in `.github/rulesets/protect-main.json` to enforce the flow:
Settings -> Rules -> Rulesets -> New ruleset -> Import, then select the file
(or create it via the REST API). It requires a pull request into `main` with
the `datasets` and `pr-policy` checks green and a code-owner review, and blocks
force-pushes and branch deletion. Repository admins keep a bypass for
emergencies. Enable "Require signed commits" in the same ruleset once all
contributors sign.

## Releasing an experiment (DOI)

Each experiment is deposited to Zenodo as its own record, so it carries its own
DOI. See `PUSH.md` (kept locally) and the `release` workflow. In short: add the
`ZENODO_TOKEN` secret, run the `release` workflow (sandbox first), take the DOI
it returns, and write it into that experiment's `CITATION.cff`, its
`zenodo.json`, and the preprint's `\mrfdoi` through the normal PR flow.
