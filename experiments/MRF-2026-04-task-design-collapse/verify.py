"""Recompute the headline statistics of MRF-2026-04 from this bundle alone.

    python3 verify.py

Two things are checked, and both read only files in this directory.

1. `records/` — the one probed cell. The pass rate, its Wilson 95%
   interval, the metered cost, and the terminating exception of the
   errored trial are recomputed from the per-trial records.

2. `dataset.json` — the consolidated gate-0 dataset the paper is written
   from. Every value in it carries a `source` and a `method`
   (`parsed` from a committed file, `derived` from one by a stated rule,
   `transcribed` from a line of a committed report, or `maintained` in
   the census). This script recounts the designs by disposition and by
   what retired them, checks those counts against the scalar keys the
   manuscript quotes, and reports the provenance mix. A disagreement
   between the recount and the quoted scalar is printed as FAIL.

The seven designs that never ran against a model have no rollouts by
construction; that is the paper's result, not a gap in this bundle.
"""
import json
import math
import pathlib
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def main():
    fails = []

    print("Probed cell")
    print("-" * 64)
    rows = []
    for f in sorted((HERE / "records").glob("*.jsonl")):
        rows += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    n = len(rows)
    passes = sum(1 for r in rows if r.get("passed"))
    errs = [r for r in rows if r.get("errored")]
    cost = sum(r.get("cli_cost_usd") or 0.0 for r in rows)
    lo, hi = wilson(passes, n)
    print(f"  trials                {n}")
    print(f"  passes                {passes}")
    print(f"  pass rate             {passes / n:.3f}  "
          f"Wilson 95% [{lo:.3f}, {hi:.3f}]")
    print(f"  errored trials        {len(errs)}"
          + (f"  ({errs[0].get('exception')})" if errs else ""))
    print(f"  metered cost (USD)    {cost:.2f}")
    for r in rows:
        agent = r.get("agent_wall_s")
        print(f"    {r['trial']:<34s} score="
              f"{'-' if r.get('score') is None else format(r['score'], '.1f')}"
              f"  cost={r.get('cli_cost_usd', 0):.2f}"
              f"  agent={'-' if agent is None else format(agent / 3600, '.2f')} h")

    ds = HERE / "dataset.json"
    if not ds.exists():
        print("\nno dataset.json in this bundle")
        return 1 if fails else 0
    d = json.loads(ds.read_text())
    values, series = d["values"], d["series"]

    print("\nDesigns, recounted from the dataset")
    print("-" * 64)
    designs = series["designs"]
    disp = Counter(x["disposition"] for x in designs)
    by = Counter(x.get("retired_by") for x in designs)
    built = sum(1 for x in designs if x.get("built"))
    print(f"  designs               {len(designs)}")
    for k, v in sorted(disp.items()):
        print(f"    disposition {k:<9s} {v}")
    for k, v in sorted(by.items(), key=lambda kv: str(kv[0])):
        print(f"    retired by {str(k):<10s} {v}")
    print(f"  built as a task        {built}")
    print(f"  never built            {len(designs) - built}")

    def check(key, got):
        want = values.get(key, {}).get("value")
        ok = want == got
        print(f"  {key:<22s} dataset={want!s:<5s} recount={got!s:<5s} "
              f"{'ok' if ok else 'FAIL'}")
        if not ok:
            fails.append(key)

    print("\nRecount against the scalars the manuscript quotes")
    print("-" * 64)
    check("n_designs", len(designs))
    check("n_fallen", disp.get("fell", 0))
    check("n_probed", by.get("probe", 0))
    check("n_retired_probe", by.get("probe", 0))
    check("n_never_probed", len(designs) - by.get("probe", 0))
    check("n_retired_argument", by.get("argument", 0))
    check("n_retired_gate0", by.get("gate-0", 0))
    check("n_built", built)
    check("n_never_built", len(designs) - built)
    check("probe_passes", passes)
    check("probe_errored", len(errs))
    check("probe_trials", n)

    print("\nProvenance of every value in the dataset")
    print("-" * 64)
    meth = Counter(v.get("method") for v in values.values())
    for k, v in sorted(meth.items()):
        print(f"  {str(k):<22s} {v}")
    print(f"  {'total':<22s} {len(values)}")
    missing = [k for k, v in values.items() if not v.get("source")
               or not v.get("method")]
    if missing:
        fails.append("provenance")
        print(f"  values with no source or method: {len(missing)}")
        for k in missing[:10]:
            print(f"    - {k}")
    else:
        print("  every value carries a source and a method")

    print()
    if fails:
        print(f"FAIL: {len(fails)} disagreement(s): {', '.join(fails)}")
        return 1
    print("OK: every recount matches the dataset.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
