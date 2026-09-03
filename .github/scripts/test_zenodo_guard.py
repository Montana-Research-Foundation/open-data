#!/usr/bin/env python3
"""Prove the Zenodo deposit guard.

    python .github/scripts/test_zenodo_guard.py

A Zenodo deposit mints a new record rather than updating one, so depositing
an experiment that already has a DOI duplicates it and orphans the DOI that
is already cited. `zenodo_deposit.py` therefore skips any experiment whose
CITATION.cff or zenodo.json records one. That skip is the thing standing
between a mistaken dispatch and a set of orphaned records, so it is tested
two ways.

Against the real `experiments/` tree, every published experiment must be
skipped, by `--all` and by name. That is the invariant that matters and it
holds whatever state the tree is in.

Against a fixture, one experiment with a DOI and one without, the selection
half is proved: the guard must skip the first and select the second. The
fixture exists because the real tree is fully published once a release
round finishes, and a test that could only run before the last DOI was
minted would stop testing anything the day it mattered most.

Every check runs `--dry-run` with ZENODO_TOKEN removed from the
environment, so this file cannot reach the network however it is invoked.
The `datasets` check runs it on every pull request.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
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


def run(*args, root=None):
    """The script in dry-run, with no token reachable.

    `root` runs a copy of the script from another tree: it resolves
    experiments/ from its own location, so the fixture needs its own copy
    rather than a changed working directory.
    """
    script = Path(root) / ".github/scripts/zenodo_deposit.py" if root else SCRIPT
    env = {k: v for k, v in os.environ.items() if k != "ZENODO_TOKEN"}
    return subprocess.run([sys.executable, str(script), *args, "--dry-run"],
                          capture_output=True, text=True, env=env,
                          cwd=root or ROOT)


CFF = """cff-version: 1.2.0
message: "If you use this data, please cite it as below."
title: "{title}"
type: dataset
authors:
  - given-names: Test
    family-names: Author
version: "1.0.0"
license: CC-BY-4.0
{doi}"""


def make_fixture(tmp):
    """Two experiments: one already published, one not."""
    exp = Path(tmp) / "experiments"
    published = exp / "MRF-0000-01-published"
    unpublished = exp / "MRF-0000-02-unpublished"
    for d, doi in ((published, "10.5281/zenodo.9999999"), (unpublished, None)):
        d.mkdir(parents=True)
        (d / "CITATION.cff").write_text(CFF.format(
            title=d.name,
            doi=f"doi: {doi}\n" if doi else "# doi: 10.5281/zenodo.XXXXXXX\n"))
        meta = {"upload_type": "dataset", "title": d.name,
                "license": "cc-by-4.0", "creators": [{"name": "Author, Test"}]}
        if doi:
            meta["doi"] = doi
        (d / "zenodo.json").write_text(json.dumps(meta, indent=2) + "\n")
    return published, unpublished


def main():
    experiments = sorted(p for p in EXP.glob("*") if p.is_dir())
    published = [p for p in experiments if zd.recorded_doi(p)]
    unpublished = [p for p in experiments if not zd.recorded_doi(p)]

    print(f"experiments/ holds {len(experiments)}: "
          f"{len(published)} with a DOI, {len(unpublished)} without")
    for p in experiments:
        print(f"  {p.name:<38s} {zd.recorded_doi(p) or '(no DOI yet)'}")

    print("\nevery published experiment is skipped, whatever the tree holds")
    r = run("--all")
    check("--all exits 0", r.returncode == 0, r.stderr.strip()[-120:])
    for p in published:
        check(f"--all skips {p.name}",
              f"{p.name}: skip, already published" in r.stdout)
        rp = run("--experiment", p.name)
        check(f"--experiment {p.name} is skipped",
              rp.returncode == 0 and "skip, already published" in rp.stdout
              and "would deposit" not in rp.stdout)
    for p in unpublished:
        check(f"--all selects {p.name}", f"{p.name}: would deposit" in r.stdout)
    check("--all reports the right split",
          f"plan: {len(unpublished)} to deposit, {len(published)} skipped"
          in r.stdout)
    check("no published experiment is ever selected",
          all(f"{p.name}: would deposit" not in r.stdout for p in published))

    print("\nthe recorded DOI lives in CITATION.cff (the concept DOI)")
    for p in published:
        cff_lines = [l for l in (p / "CITATION.cff").read_text().splitlines()
                     if not l.strip().startswith("#")]
        by_cff = any(l.strip().startswith("doi:") for l in cff_lines)
        check(f"{p.name} records its DOI in CITATION.cff", by_cff)
        # zenodo.json deliberately carries no doi key: each deposited
        # version receives its own version DOI from Zenodo, and the
        # concept DOI in CITATION.cff needs no write-back.
        check(f"{p.name} zenodo.json carries no doi key",
              "doi" not in json.loads((p / "zenodo.json").read_text()))

    print("\n--new-version selects only an already published experiment")
    for p in published[:1]:
        r = run("--experiment", p.name, "--new-version")
        check(f"--new-version selects {p.name}",
              r.returncode == 0 and "would deposit a new version of"
              in r.stdout and "skip, already published" not in r.stdout)
    r = run("--all", "--new-version")
    check("--new-version with --all exits non-zero", r.returncode != 0)
    r = run("--new-version")
    check("--new-version with no experiment exits non-zero",
          r.returncode != 0)

    print("\nfixture: one published, one not")
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(ROOT / ".github", Path(tmp) / ".github")
        pub, unpub = make_fixture(tmp)
        r = run("--all", root=tmp)
        check("fixture --all exits 0", r.returncode == 0,
              r.stderr.strip()[-120:])
        check("fixture skips the published one",
              f"{pub.name}: skip, already published as 10.5281/zenodo.9999999"
              in r.stdout)
        check("fixture selects the unpublished one",
              f"{unpub.name}: would deposit" in r.stdout)
        check("fixture split is 1 and 1",
              "plan: 1 to deposit, 1 skipped" in r.stdout)
        rp = run("--experiment", pub.name, root=tmp)
        check("fixture skips the published one by name",
              "skip, already published" in rp.stdout
              and "would deposit" not in rp.stdout)
        rp = run("--experiment", unpub.name, root=tmp)
        check("fixture selects the unpublished one by name",
              f"{unpub.name}: would deposit" in rp.stdout)
        rp = run("--experiment", f"experiments/{unpub.name}", root=tmp)
        check("a path works as well as a bare name",
              f"{unpub.name}: would deposit" in rp.stdout)
        rp = run("--experiment", pub.name, "--new-version", root=tmp)
        check("fixture --new-version selects the published one",
              rp.returncode == 0
              and "would deposit a new version of 10.5281/zenodo.9999999"
              in rp.stdout)
        rp = run("--experiment", unpub.name, "--new-version", root=tmp)
        check("fixture --new-version refuses the unpublished one",
              rp.returncode != 0 and "would deposit" not in rp.stdout)

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
    print(f"OK: {len(published)} published experiment(s) skipped, and the "
          f"fixture proves an unpublished one is still selected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
