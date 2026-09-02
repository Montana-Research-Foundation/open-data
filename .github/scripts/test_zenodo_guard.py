#!/usr/bin/env python3
"""Prove the Zenodo deposit guard on the real experiments/ tree.

    python .github/scripts/test_zenodo_guard.py

A Zenodo deposit mints a new record rather than updating one, so depositing
an experiment that already has a DOI duplicates it and orphans the DOI that
is already cited. `zenodo_deposit.py` therefore skips any experiment whose
CITATION.cff or zenodo.json records one. That skip is the thing standing
between a mistaken dispatch and three orphaned records, so it is tested
against the tree as it actually is rather than against a fixture.

Every check runs `--dry-run`, with ZENODO_TOKEN removed from the
environment, so this file cannot reach the network however it is invoked.
The `datasets` check runs it on every pull request.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/scripts/zenodo_deposit.py"
EXP = ROOT / "experiments"

sys.path.insert(0, str(SCRIPT.parent))
import zenodo_deposit as zd  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
    if not ok:
        failures.append(label)


def run(*args):
    """The script in dry-run, with no token reachable."""
    env = {k: v for k, v in os.environ.items() if k != "ZENODO_TOKEN"}
    return subprocess.run([sys.executable, str(SCRIPT), *args, "--dry-run"],
                          capture_output=True, text=True, env=env, cwd=ROOT)


def main():
    experiments = sorted(p for p in EXP.glob("*") if p.is_dir())
    published = [p for p in experiments if zd.recorded_doi(p)]
    unpublished = [p for p in experiments if not zd.recorded_doi(p)]

    print(f"experiments/ holds {len(experiments)}: "
          f"{len(published)} with a DOI, {len(unpublished)} without")
    for p in experiments:
        print(f"  {p.name:<38s} {zd.recorded_doi(p) or '(no DOI yet)'}")

    print("\nthe tree is in the state this guard exists for")
    check("at least one experiment already has a DOI", bool(published))
    check("at least one experiment has none", bool(unpublished))

    print("\nrecorded_doi reads both files")
    for p in published:
        cff = "doi:" in "\n".join(
            l for l in (p / "CITATION.cff").read_text().splitlines()
            if not l.strip().startswith("#"))
        zj = bool((json.loads((p / "zenodo.json").read_text()).get("doi") or ""))
        check(f"{p.name} carries a DOI in CITATION.cff and zenodo.json",
              cff and zj)
    for p in unpublished:
        text = (p / "CITATION.cff").read_text()
        check(f"{p.name} has only the commented placeholder",
              "# doi:" in text and not any(
                  l.strip().startswith("doi:") for l in text.splitlines()))

    print("\n--all deposits only what has no DOI")
    r = run("--all")
    check("--all exits 0", r.returncode == 0, r.stderr.strip()[-120:])
    for p in published:
        check(f"--all skips {p.name}", f"{p.name}: skip, already published" in r.stdout)
    for p in unpublished:
        check(f"--all selects {p.name}", f"{p.name}: would deposit" in r.stdout)
    check("--all reports the right split",
          f"plan: {len(unpublished)} to deposit, {len(published)} skipped" in r.stdout)

    print("\n--experiment selects one, and the guard still applies")
    for p in unpublished:
        r = run("--experiment", p.name)
        check(f"--experiment {p.name} is selected",
              r.returncode == 0 and f"{p.name}: would deposit" in r.stdout)
    for p in published:
        r = run("--experiment", p.name)
        check(f"--experiment {p.name} is skipped",
              r.returncode == 0 and "skip, already published" in r.stdout
              and "would deposit" not in r.stdout)
    if unpublished:
        p = unpublished[0]
        r = run("--experiment", f"experiments/{p.name}")
        check("a path works as well as a bare name",
              r.returncode == 0 and f"{p.name}: would deposit" in r.stdout)

    print("\nselecting nothing is an error, never a fallback to everything")
    r = run()
    check("no selector exits non-zero", r.returncode != 0)
    check("no selector deposits nothing", "would deposit" not in r.stdout)
    r = run("--all", "--experiment", experiments[0].name)
    check("--all with --experiment exits non-zero", r.returncode != 0)
    r = run("--experiment", "MRF-9999-does-not-exist")
    check("an unknown experiment exits non-zero", r.returncode != 0)

    print("\ndry-run needs no token")
    check("ZENODO_TOKEN is absent from the checks above",
          "ZENODO_TOKEN is not set" not in run("--all").stdout)

    print()
    if failures:
        print(f"FAIL: {len(failures)} check(s): {', '.join(failures)}")
        return 1
    print("OK: the guard skips every published experiment and selects only "
          "the unpublished one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
