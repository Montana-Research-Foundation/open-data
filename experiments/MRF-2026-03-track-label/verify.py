"""Recompute the headline statistics from records/ alone.

    python3 verify.py

Reads the aggregate per-rollout records and recomputes, per cell, the
pass rate and its Wilson 95% interval; for the track-label bundle it also
recomputes the confirmatory reasoning-token effect (paired d and the
exact two-sided signed-rank p) from the matched seeds. No task content is
needed; the withheld transcripts are not used. Values are printed for
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


def signed_rank_p(diffs):
    d = [x for x in diffs if x != 0]
    n = len(d)
    if n == 0:
        return 1.0
    order = sorted(range(n), key=lambda i: abs(d[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(d[order[j + 1]]) == abs(d[order[i]]):
            j += 1
        for t in range(i, j + 1):
            ranks[order[t]] = (i + j + 2) / 2
        i = j + 1
    r2 = [int(round(2 * r)) for r in ranks]
    total = sum(r2)
    counts = [0] * (total + 1)
    counts[0] = 1
    for rk in r2:
        for w in range(total, rk - 1, -1):
            counts[w] += counts[w - rk]
    wpos = sum(r for x, r in zip(d, ranks) if x > 0)
    lo = int(round(2 * min(wpos, sum(ranks) - wpos)))
    tail = sum(counts[w] for w in range(total + 1) if w <= lo or w >= total - lo)
    return round(min(1.0, tail / 2 ** n), 4)


def paired_d(diffs):
    n = len(diffs)
    if n < 2:
        return None
    m = sum(diffs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in diffs) / (n - 1))
    return None if sd == 0 else round(m / sd, 4)


def rates():
    print("== per-cell pass rate (Wilson 95%) ==")
    for f in sorted(REC.glob("*.jsonl")):
        rows = load(f.stem)
        k = sum(1 for r in rows if r["passed"])
        print(f"  {f.stem:52s} {k}/{len(rows)}  {wilson(k, len(rows))}")


def paired(cell_a, cell_b, key="thinking_tokens", label=""):
    a = {r["seed"]: r for r in load(cell_a)}
    b = {r["seed"]: r for r in load(cell_b)}
    seeds = sorted(set(a) & set(b))
    diffs = [a[s][key] - b[s][key] for s in seeds
             if a[s].get(key) is not None and b[s].get(key) is not None]
    if not diffs:
        return
    print(f"  {label}: n={len(diffs)}  paired d={paired_d(diffs)}  "
          f"exact signed-rank p={signed_rank_p(diffs)}")


if __name__ == "__main__":
    rates()
    # track-label confirmatory stage 5 (present only in that bundle)
    for cfg, drv in (("Opus 5", "cli"), ("GPT-5.6 Sol", "gpt")):
        a = f"protocol-induction-track5-remedial-individual-{drv}"
        b = f"protocol-induction-track5-standard-individual-{drv}"
        if (REC / f"{a}.jsonl").exists():
            print(f"\n== stage-5 reasoning-token effect, {cfg} ==")
            paired(a, b, "thinking_tokens", "remedial vs standard")
