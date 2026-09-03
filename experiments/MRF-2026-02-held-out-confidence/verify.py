"""Recompute the headline statistics from records/ alone.

    python3 verify.py

Reads the aggregate per-rollout records and recomputes, per cell, the
pass rate and its Wilson 95% interval;
for cells whose records carry a declared confidence it also recomputes the
mean declaration and the overconfidence gap (mean declared confidence minus
the pass rate, both computed over the declaring rollouts; a rollout that
recorded no declaration is excluded from both terms).
The pass rule is: `passed` iff `score` >= 0.5. The script re-derives the
flag from `score` on every record and stops on any disagreement with the
stored value, so the rule is checked rather than trusted. No task content
is needed; the withheld transcripts are not used. Values are printed for
comparison against the paper.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
REC = HERE / "records"
Z = 1.959964


def load(cell):
    f = REC / f"{cell}.jsonl"
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()]


def wilson(k, n):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (round((c - h) / d, 4), round((c + h) / d, 4))


def rates():
    print("== per-cell pass rate (Wilson 95%); pass rule: score >= 0.5 ==")
    bad = []
    for f in sorted(REC.glob("*.jsonl")):
        rows = load(f.stem)
        for r in rows:
            if bool(r.get("passed")) != ((r.get("score") or 0) >= 0.5):
                bad.append(f"{f.stem} seed {r.get('seed')}")
        k = sum(1 for r in rows if r["passed"])
        line = f"  {f.stem:52s} {k}/{len(rows)}  {wilson(k, len(rows))}"
        dec = [(r["metrics"]["declared_confidence"], r["passed"])
               for r in rows if isinstance(r.get("metrics"), dict)
               and r["metrics"].get("declared_confidence") is not None]
        if dec:
            mc = sum(c for c, _ in dec) / len(dec)
            pr = sum(1 for _, p in dec if p) / len(dec)
            line += (f"\n    {'':50s} mean declared confidence "
                     f"{mc:.4f} (n={len(dec)})  "
                     f"gap {mc - pr:+.4f}")
        print(line)
    if bad:
        raise SystemExit("FAIL: stored `passed` disagrees with the pass "
                         "rule score >= 0.5 on: " + ", ".join(bad))


if __name__ == "__main__":
    rates()
