# Security and data policy

## What this repository does and does not contain

This repository publishes **aggregate** reproducibility data: per-rollout
outcome records and self-contained verification scripts. It deliberately
withholds, under contamination control, the task families, the raw agent
transcripts, the induced rules, the held-out grading data, and the evaluation
seed ranges (see each experiment's `WITHHELD.md`). Nothing here is a secret or
a credential.

## Reporting a problem

- **Data errors** (a wrong number, a mismatch a paper's claim): open a *Data
  correction* issue.
- **A suspected leak** (task content or anything that should have been
  withheld appearing in a shipped file), or any security concern: use GitHub's
  private vulnerability reporting (Security -> Report a vulnerability) rather
  than a public issue. Do not attach the sensitive content to a public thread.

## Integrity

Every experiment ships a `MANIFEST.sha256`; CI recomputes it on each pull
request, so altered data fails validation. Commits are GPG-signed, and the
default branch is protected against force-pushes and deletion.
