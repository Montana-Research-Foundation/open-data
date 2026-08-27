#!/usr/bin/env python3
"""Deposit experiments to Zenodo, one record (and DOI) per experiment.

Reads experiments/<name>/zenodo.json as the deposition metadata, uploads
every file in the experiment, and (with --publish) publishes to mint the DOI.
Token from the ZENODO_TOKEN environment variable.

  export ZENODO_TOKEN=...            # Zenodo personal access token
  # test on the sandbox first (separate account + token at sandbox.zenodo.org):
  python .github/scripts/zenodo_deposit.py --all --base-url https://sandbox.zenodo.org
  # for real, when ready:
  python .github/scripts/zenodo_deposit.py --all --base-url https://zenodo.org --publish --write-doi

--write-doi patches each experiment's CITATION.cff and zenodo.json with the
minted DOI. In CI the DOIs are written to --out and the step summary instead,
and a maintainer applies them through the normal issue -> branch -> PR flow.
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
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--experiment", help="a single experiments/<name> path")
    ap.add_argument("--base-url", default="https://sandbox.zenodo.org")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--write-doi", action="store_true")
    ap.add_argument("--summary")
    ap.add_argument("--out")
    args = ap.parse_args()

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        sys.exit("ZENODO_TOKEN is not set.")

    if args.all:
        targets = sorted(p for p in EXP.glob("*") if p.is_dir())
    elif args.experiment:
        targets = [Path(args.experiment)]
    else:
        sys.exit("pass --all or --experiment <path>")

    results = []
    for exp in targets:
        r = deposit_one(exp, token, args.base_url.rstrip("/"), args.publish)
        results.append(r)
        print(f"{r['experiment']}: doi={r['doi']} (deposit {r['deposit_id']}, "
              f"published={r['published']})")
        if args.write_doi and r["doi"]:
            write_doi(exp, r["doi"])
    if args.out:
        Path(args.out).write_text(json.dumps(results, indent=2) + "\n")
    if args.summary:
        with open(args.summary, "a") as fh:
            fh.write("\n| experiment | DOI | deposit |\n|---|---|---|\n")
            for r in results:
                fh.write(f"| {r['experiment']} | {r['doi'] or '(unpublished)'} "
                         f"| {r['html'] or r['deposit_id']} |\n")


if __name__ == "__main__":
    main()
