#!/usr/bin/env python3
"""Deposit experiments to Zenodo, one record (and DOI) per experiment.

Reads experiments/<name>/zenodo.json as the deposition metadata, uploads
every file in the experiment, and (with --publish) publishes to mint the DOI.
Token from the ZENODO_TOKEN environment variable.

  export ZENODO_TOKEN=...            # Zenodo personal access token
  # see what would be deposited, with no token and no network:
  python .github/scripts/zenodo_deposit.py --all --dry-run
  # test on the sandbox first (separate account + token at sandbox.zenodo.org):
  python .github/scripts/zenodo_deposit.py --experiment MRF-2026-04-task-design-collapse \
      --base-url https://sandbox.zenodo.org
  # for real, when ready:
  python .github/scripts/zenodo_deposit.py --experiment MRF-2026-04-task-design-collapse \
      --base-url https://zenodo.org --publish --write-doi

An experiment whose CITATION.cff or zenodo.json already records a DOI is
never deposited as a NEW record. A plain deposit mints a new record, so
re-running over a published experiment would not update it, it would
duplicate it and orphan the DOI that is already cited. The plain-deposit
skip is unconditional.

Releasing a revision of a published experiment is the separate,
deliberate `--new-version` path:

  python .github/scripts/zenodo_deposit.py --experiment <name> \
      --new-version --base-url https://zenodo.org --publish

It requires the experiment to record a DOI (the concept DOI, which
resolves to the latest version), creates a new version of that record
through the Zenodo versioning API, replaces its files with the current
bundle zip, and updates the metadata from zenodo.json. The concept DOI
never changes, which is why the shipped CITATION.cff carries it: the
files inside a deposit can name their own citable DOI before the
version is minted, so a deposit can never again archive files that
disclaim their own identifier (the failure the 2026-09-03 release audit
found in every v1.0.0 record). Each new version additionally receives
its own version DOI from Zenodo at publish time; it is reported in the
output and needs no write-back into the repository.

--write-doi (first deposits only) patches the experiment's CITATION.cff
with the minted concept DOI. In CI the DOIs are written to --out and the
step summary instead, and a maintainer applies them through the normal
issue -> branch -> PR flow.
"""
import argparse
import io
import json
import os
import sys
import zipfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"


def api(method, url, token, data=None, headers=None):
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(f"{url}{sep}access_token={token}", method=method)
    req.add_header("Accept", "application/json")
    body = None
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if data is not None and not isinstance(data, (bytes, bytearray)):
        req.add_header("Content-Type", "application/json")
        body = json.dumps(data).encode()
    else:
        body = data
    try:
        with urllib.request.urlopen(req, body) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"Zenodo API {method} {url} -> {e.code}: {e.read().decode()[:500]}")


def recorded_doi(exp):
    """The DOI this experiment already carries, or None.

    Two files can hold it and either one counts. In CITATION.cff the minted
    form is an uncommented `doi:` line; the unminted form is the commented
    placeholder the bundle generator writes, which must not match. In
    zenodo.json it is a non-empty "doi" key.
    """
    cff = exp / "CITATION.cff"
    if cff.exists():
        for line in cff.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if stripped.startswith("doi:"):
                value = stripped[4:].strip().strip('"\'')
                if value:
                    return value
    zj = exp / "zenodo.json"
    if zj.exists():
        try:
            value = (json.loads(zj.read_text()).get("doi") or "").strip()
        except (json.JSONDecodeError, AttributeError):
            value = ""
        if value:
            return value
    return None


def resolve_experiment(name):
    """Accept a bare directory name or a path under experiments/."""
    candidate = Path(name)
    if candidate.is_dir():
        return candidate.resolve()
    candidate = EXP / Path(name).name
    if candidate.is_dir():
        return candidate
    available = ", ".join(sorted(p.name for p in EXP.glob("*") if p.is_dir()))
    sys.exit(f"no such experiment: {name}\navailable: {available}")


def plan(all_experiments, experiment, new_version=False):
    """Resolve the selection into (to_deposit, skipped) without any network.

    `skipped` is a list of (experiment, doi) for the ones already published.
    With --new-version the requirement inverts: the one named experiment
    must already record a DOI (the record to version), and an experiment
    with no DOI is an error, never a fallback to a first deposit.
    """
    if all_experiments and experiment:
        sys.exit("pass --all or --experiment, not both")
    if new_version:
        if all_experiments or not experiment:
            sys.exit("--new-version takes exactly one --experiment <name>: "
                     "a version release names the record it revises")
        exp = resolve_experiment(experiment)
        if not recorded_doi(exp):
            sys.exit(f"{exp.name} records no DOI, so there is no published "
                     "record to version; a first release is a plain deposit")
        return [exp], []
    if all_experiments:
        targets = sorted((p for p in EXP.glob("*") if p.is_dir()),
                         key=lambda p: p.name)
    elif experiment:
        targets = [resolve_experiment(experiment)]
    else:
        sys.exit("pass --all or --experiment <name>")
    to_deposit, skipped = [], []
    for exp in targets:
        doi = recorded_doi(exp)
        (skipped.append((exp, doi)) if doi else to_deposit.append(exp))
    return to_deposit, skipped


def zip_experiment(exp):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(p for p in exp.rglob("*") if p.is_file()):
            z.write(f, f"{exp.name}/{f.relative_to(exp).as_posix()}")
    return buf.getvalue()


def deposit_one(exp, token, base_url, publish):
    meta = json.loads((exp / "zenodo.json").read_text())
    dep = api("POST", f"{base_url}/api/deposit/depositions", token, {"metadata": meta})
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    # Zenodo bucket keys are flat (nested paths 404), so upload the whole
    # experiment as a single zip that preserves its internal structure.
    api("PUT", f"{bucket}/{exp.name}.zip", token, data=zip_experiment(exp),
        headers={"Content-Type": "application/octet-stream"})
    prereserved = dep.get("metadata", {}).get("prereserve_doi", {}).get("doi")
    if publish:
        pub = api("POST",
                  f"{base_url}/api/deposit/depositions/{dep_id}/actions/publish", token)
        doi = pub.get("doi") or prereserved
    else:
        doi = prereserved
    return {"experiment": exp.name, "deposit_id": dep_id, "doi": doi,
            "published": bool(publish), "html": dep["links"].get("html")}


def new_version_one(exp, token, base_url, publish):
    """Create, upload, and optionally publish a new version of a record.

    The recorded DOI is the concept DOI; resolving its record id through
    the public records API yields the latest published version, whose
    deposition the versioning action forks. The inherited files are
    removed so the new version carries exactly the current bundle zip,
    and the metadata is replaced from zenodo.json (which carries the new
    bundle version and publication date).
    """
    concept = recorded_doi(exp)
    recid = concept.rsplit(".", 1)[-1]
    latest = api("GET", f"{base_url}/api/records/{recid}", token)
    latest_id = latest["id"]
    nv = api("POST", f"{base_url}/api/deposit/depositions/{latest_id}"
                     "/actions/newversion", token)
    draft_url = nv.get("links", {}).get("latest_draft")
    if not draft_url:
        sys.exit(f"{exp.name}: newversion returned no draft link")
    draft = api("GET", draft_url, token)
    dep_id = draft["id"]
    for f in api("GET", f"{base_url}/api/deposit/depositions/{dep_id}/files",
                 token):
        api("DELETE",
            f"{base_url}/api/deposit/depositions/{dep_id}/files/{f['id']}",
            token)
    meta = json.loads((exp / "zenodo.json").read_text())
    api("PUT", f"{base_url}/api/deposit/depositions/{dep_id}", token,
        {"metadata": meta})
    draft = api("GET", f"{base_url}/api/deposit/depositions/{dep_id}", token)
    bucket = draft["links"]["bucket"]
    api("PUT", f"{bucket}/{exp.name}.zip", token, data=zip_experiment(exp),
        headers={"Content-Type": "application/octet-stream"})
    prereserved = draft.get("metadata", {}).get("prereserve_doi", {}).get("doi")
    if publish:
        pub = api("POST", f"{base_url}/api/deposit/depositions/{dep_id}"
                          "/actions/publish", token)
        doi = pub.get("doi") or prereserved
    else:
        doi = prereserved
    return {"experiment": exp.name, "deposit_id": dep_id, "doi": doi,
            "concept_doi": concept, "published": bool(publish),
            "html": draft["links"].get("html")}


def write_doi(exp, doi):
    cff = exp / "CITATION.cff"
    text = cff.read_text()
    if "\ndoi:" not in text:
        text = text.replace("# doi: 10.5281/zenodo.XXXXXXX", f"doi: {doi}")
        if f"doi: {doi}" not in text:
            text += f"doi: {doi}\n"
        cff.write_text(text)
    zj = exp / "zenodo.json"
    meta = json.loads(zj.read_text())
    meta["doi"] = doi
    zj.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="every experiment that has no DOI yet")
    ap.add_argument("--experiment",
                    help="one experiment, by directory name or path")
    ap.add_argument("--base-url", default="https://sandbox.zenodo.org")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--write-doi", action="store_true")
    ap.add_argument("--new-version", action="store_true",
                    help="deposit a new version of the one named, already "
                         "published experiment instead of a new record")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and stop: no token, no network")
    ap.add_argument("--summary")
    ap.add_argument("--out")
    args = ap.parse_args()

    to_deposit, skipped = plan(args.all, args.experiment, args.new_version)

    verb = "deposit a new version of" if args.new_version else "deposit"
    for exp, doi in skipped:
        print(f"{exp.name}: skip, already published as {doi}")
    for exp in to_deposit:
        print(f"{exp.name}: would {verb}"
              + (f" {recorded_doi(exp)}" if args.new_version else "")
              if args.dry_run else f"{exp.name}: depositing"
              + (" a new version" if args.new_version else ""))

    if args.dry_run:
        print(f"\nplan: {len(to_deposit)} to {verb.split()[0]}"
              + (" (new version)" if args.new_version else "")
              + f", {len(skipped)} skipped "
              f"(target {args.base_url}, publish={args.publish})")
        if args.summary:
            with open(args.summary, "a") as fh:
                fh.write("\n| experiment | plan |\n|---|---|\n")
                for exp, doi in skipped:
                    fh.write(f"| {exp.name} | skip, published as {doi} |\n")
                for exp in to_deposit:
                    fh.write(f"| {exp.name} | would {verb} |\n")
        return
    if not to_deposit:
        print("nothing to deposit: every selected experiment already has a DOI.")
        return

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        sys.exit("ZENODO_TOKEN is not set.")

    results = []
    for exp in to_deposit:
        if args.new_version:
            r = new_version_one(exp, token, args.base_url.rstrip("/"),
                                args.publish)
        else:
            r = deposit_one(exp, token, args.base_url.rstrip("/"), args.publish)
        results.append(r)
        print(f"{r['experiment']}: doi={r['doi']} (deposit {r['deposit_id']}, "
              f"published={r['published']})")
        if args.write_doi and r["doi"] and not args.new_version:
            write_doi(exp, r["doi"])
    if args.out:
        Path(args.out).write_text(json.dumps(results, indent=2) + "\n")
    if args.summary:
        with open(args.summary, "a") as fh:
            fh.write("\n| experiment | DOI | deposit |\n|---|---|---|\n")
            for exp, doi in skipped:
                fh.write(f"| {exp.name} | {doi} | skipped, already published |\n")
            for r in results:
                fh.write(f"| {r['experiment']} | {r['doi'] or '(unpublished)'} "
                         f"| {r['html'] or r['deposit_id']} |\n")


if __name__ == "__main__":
    main()
