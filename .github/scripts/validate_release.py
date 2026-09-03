#!/usr/bin/env python3
"""Validate the open-data release.

Checks, per experiment under experiments/:
  - required files are present;
  - MANIFEST.sha256 matches every file, and no file is unlisted (integrity);
  - verify.py runs to completion (returns 0);
  - CITATION.cff is valid and complete; zenodo.json is valid dataset metadata;
  - the README rollout count matches the actual record line count;
  - no leak: absolute local paths or private key blocks. (The
    contamination canary is deliberately NOT checked here: embedding its
    marker in a public validator would itself publish the canary. The
    canary scan runs in the private repository before a release.)

Run in CI and locally:  python .github/scripts/validate_release.py
Exits non-zero if anything fails, after printing every failure.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
REQUIRED = ["records", "verify.py", "CITATION.cff", "zenodo.json",
            "WITHHELD.md", "LICENSE", "MANIFEST.sha256", "README.md"]
LEAK = re.compile(r"/Users/|/home/[^/\s]+/|BEGIN [A-Z ]*PRIVATE KEY")

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_structure(exp, errs):
    for name in REQUIRED:
        if not (exp / name).exists():
            errs.append(f"{exp.name}: missing required {name}")


def check_manifest(exp, errs):
    man = exp / "MANIFEST.sha256"
    if not man.exists():
        return
    listed = set()
    for line in man.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        digest, _, rel = line.partition("  ")
        rel = rel.strip()
        listed.add(rel)
        f = exp / rel
        if not f.exists():
            errs.append(f"{exp.name}: manifest lists missing file {rel}")
        elif sha256(f) != digest:
            errs.append(f"{exp.name}: sha256 mismatch for {rel}")
    for f in exp.rglob("*"):
        if f.is_file():
            rel = f.relative_to(exp).as_posix()
            if rel != "MANIFEST.sha256" and rel not in listed:
                errs.append(f"{exp.name}: file not covered by manifest: {rel}")


def check_verify(exp, errs):
    vp = exp / "verify.py"
    if not vp.exists():
        return
    r = subprocess.run([sys.executable, "verify.py"], cwd=exp,
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        errs.append(f"{exp.name}: verify.py exit {r.returncode}: {r.stderr.strip()[-300:]}")


def check_citation(exp, errs):
    f = exp / "CITATION.cff"
    if not f.exists():
        return
    if HAVE_YAML:
        try:
            d = yaml.safe_load(f.read_text())
        except Exception as e:  # noqa: BLE001
            errs.append(f"{exp.name}: CITATION.cff not valid YAML: {e}")
            return
        for key in ("cff-version", "title", "authors", "type", "license"):
            if not d.get(key):
                errs.append(f"{exp.name}: CITATION.cff missing {key}")
    elif "title:" not in f.read_text():
        errs.append(f"{exp.name}: CITATION.cff has no title (install pyyaml for full check)")


def check_zenodo(exp, errs):
    f = exp / "zenodo.json"
    if not f.exists():
        return
    try:
        d = json.loads(f.read_text())
    except json.JSONDecodeError as e:
        errs.append(f"{exp.name}: zenodo.json not valid JSON: {e}")
        return
    if d.get("upload_type") != "dataset":
        errs.append(f"{exp.name}: zenodo.json upload_type must be 'dataset'")
    if d.get("license") != "cc-by-4.0":
        errs.append(f"{exp.name}: zenodo.json license must be 'cc-by-4.0'")
    if not d.get("creators"):
        errs.append(f"{exp.name}: zenodo.json has no creators")


def record_rollups(exp):
    total = 0
    for f in (exp / "records").glob("*.jsonl"):
        total += sum(1 for line in f.read_text().splitlines() if line.strip())
    return total


def check_readme_counts(errs):
    readme = (ROOT / "README.md").read_text()
    for exp in sorted(EXP.glob("*")):
        if not exp.is_dir():
            continue
        m = re.search(rf"\({re.escape('experiments/' + exp.name)}/\)\s*\|[^|]*\|\s*(\d+)\s*\|",
                      readme)
        if not m:
            errs.append(f"README: no table row for {exp.name}")
            continue
        claimed = int(m.group(1))
        actual = record_rollups(exp)
        if claimed != actual:
            errs.append(f"README: {exp.name} claims {claimed} rollouts, records hold {actual}")


def check_leaks(exp, errs):
    for f in exp.rglob("*"):
        if not f.is_file() or f.name == "MANIFEST.sha256":
            continue
        try:
            text = f.read_text()
        except (UnicodeDecodeError, ValueError):
            continue
        if LEAK.search(text):
            errs.append(f"{exp.name}: leak pattern in {f.relative_to(exp).as_posix()}")


def main():
    if not EXP.is_dir():
        print("FAIL: experiments/ directory not found")
        return 1
    errs = []
    experiments = sorted(p for p in EXP.glob("*") if p.is_dir())
    if not experiments:
        print("FAIL: no experiments found")
        return 1
    for exp in experiments:
        check_structure(exp, errs)
        check_manifest(exp, errs)
        check_verify(exp, errs)
        check_citation(exp, errs)
        check_zenodo(exp, errs)
        check_leaks(exp, errs)
    check_readme_counts(errs)
    if not HAVE_YAML:
        print("note: pyyaml not installed; CITATION.cff checked shallowly")
    if errs:
        print(f"FAIL: {len(errs)} problem(s):")
        for e in errs:
            print("  -", e)
        return 1
    print(f"OK: {len(experiments)} experiment(s) validated "
          f"({sum(record_rollups(e) for e in experiments)} rollouts).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
