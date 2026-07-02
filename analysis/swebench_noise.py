#!/usr/bin/env python3
"""Re-analysis of SWE-bench leaderboard per-instance results with error bars.

Zero-compute: uses the per-instance `results/results.json` files that
submissions publish in the SWE-bench/experiments repository. No agent is
re-run; this is purely the statistics the leaderboard omits.

Usage:
    python analysis/swebench_noise.py --experiments-dir /path/to/experiments \
        [--split verified] [--top 15]

Questions answered:
  1. For adjacent leaderboard entries, is the gap statistically real?
     (Exact McNemar on discordant pairs — the correct paired test.)
  2. What is the benchmark's minimal detectable difference at its N,
     given the observed discordance between nearby systems?
  3. What fraction of nearby pairs (within 5 points) are indistinguishable?

Caveats printed with the output: adjacent-rank comparisons on an observed
ranking involve selection effects (comparing order statistics); p-values are
per-pair and unadjusted. Both make the leaderboard look BETTER than it is,
so the noise findings here are conservative.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evalstats import (  # noqa: E402
    discordant_counts,
    mcnemar_pvalue,
    mdd_paired,
    paired_diff_ci,
    wilson_ci,
)

SPLIT_SIZES = {"verified": 500, "lite": 300, "test": 2294}


def load_submissions(experiments_dir: Path, split: str) -> dict[str, set[str]]:
    """Load {submission_name: set(resolved instance ids)} for a split."""
    split_dir = experiments_dir / "evaluation" / split
    if not split_dir.is_dir():
        raise SystemExit(f"not found: {split_dir}")

    submissions: dict[str, set[str]] = {}
    skipped: list[str] = []
    for sub_dir in sorted(split_dir.iterdir()):
        results_file = sub_dir / "results" / "results.json"
        if not results_file.is_file():
            continue
        try:
            data = json.loads(results_file.read_text())
        except (json.JSONDecodeError, OSError):
            skipped.append(sub_dir.name)
            continue
        resolved = data.get("resolved")
        if not isinstance(resolved, list):
            skipped.append(sub_dir.name)
            continue
        submissions[sub_dir.name] = set(resolved)

    if skipped:
        print(f"[skipped {len(skipped)} submissions with missing/atypical results.json]")
    return submissions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments-dir", type=Path, required=True)
    parser.add_argument("--split", default="verified", choices=SPLIT_SIZES)
    parser.add_argument("--top", type=int, default=15, help="rows of the adjacent-pairs table")
    parser.add_argument("--near", type=float, default=0.05, help="'nearby pair' threshold in proportion points")
    args = parser.parse_args()

    n_total = SPLIT_SIZES[args.split]
    subs = load_submissions(args.experiments_dir, args.split)
    if len(subs) < 2:
        raise SystemExit("need at least two submissions")

    for name, resolved in subs.items():
        if len(resolved) > n_total:
            print(f"[warn] {name}: {len(resolved)} resolved > split size {n_total}")

    ranked = sorted(subs.items(), key=lambda kv: len(kv[1]), reverse=True)
    print(f"\nSWE-bench {args.split}: {len(ranked)} submissions with per-instance results, N={n_total}\n")

    # ── Top-of-leaderboard with Wilson CIs ────────────────────────────────
    print(f"Top {args.top} by resolve rate (95% Wilson CI):")
    for name, resolved in ranked[: args.top]:
        k = len(resolved)
        lo, hi = wilson_ci(k, n_total)
        print(f"  {k / n_total:6.1%}  [{lo:6.1%}, {hi:6.1%}]  {name}")

    # ── Adjacent-pair tests ───────────────────────────────────────────────
    print(f"\nAdjacent leaderboard pairs (top {args.top}), exact McNemar:")
    print(f"  {'gap':>6}  {'A-only':>6} {'B-only':>6}  {'p':>8}  verdict")
    adjacent_rows = []
    for (name_a, res_a), (name_b, res_b) in zip(ranked, ranked[1:]):
        b, c = discordant_counts(res_a, res_b)
        p = mcnemar_pvalue(b, c)
        gap = (len(res_a) - len(res_b)) / n_total
        discordance = (b + c) / n_total
        adjacent_rows.append((name_a, name_b, gap, b, c, p, discordance))

    for name_a, name_b, gap, b, c, p, _ in adjacent_rows[: args.top]:
        verdict = "distinguishable" if p < 0.05 else "NOISE at N=%d" % n_total
        print(f"  {gap:6.1%}  {b:6d} {c:6d}  {p:8.3f}  {verdict}")
        print(f"          {name_a}")
        print(f"          vs {name_b}")

    # ── Aggregates ────────────────────────────────────────────────────────
    all_pairs_near = []
    for i, (name_a, res_a) in enumerate(ranked):
        for name_b, res_b in ranked[i + 1 :]:
            gap = (len(res_a) - len(res_b)) / n_total
            if gap > args.near:
                break  # ranked: every later entry is even further
            b, c = discordant_counts(res_a, res_b)
            all_pairs_near.append((gap, mcnemar_pvalue(b, c), (b + c) / n_total))

    n_adj = len(adjacent_rows)
    n_adj_noise = sum(1 for r in adjacent_rows if r[5] >= 0.05)
    discordances = sorted(r[6] for r in adjacent_rows)
    med_disc = discordances[len(discordances) // 2]

    biggest_noise_gap = max((r[2] for r in adjacent_rows if r[5] >= 0.05), default=0.0)
    smallest_real_gap = min((r[2] for r in adjacent_rows if r[5] < 0.05), default=float("nan"))

    print("\n── Aggregates ──────────────────────────────────────────────")
    print(f"Adjacent pairs indistinguishable at p>=0.05: {n_adj_noise}/{n_adj} ({n_adj_noise / n_adj:.0%})")
    if all_pairs_near:
        noise_near = sum(1 for _, p, _ in all_pairs_near if p >= 0.05)
        print(
            f"All pairs within {args.near:.0%}: {noise_near}/{len(all_pairs_near)} "
            f"({noise_near / len(all_pairs_near):.0%}) indistinguishable"
        )
    print(f"Median adjacent-pair discordance: {med_disc:.1%}")
    print(f"  -> minimal detectable difference at N={n_total}, 80% power: "
          f"{mdd_paired(n_total, med_disc):.1%}")
    print(f"Largest adjacent gap that is still noise:  {biggest_noise_gap:.1%}")
    print(f"Smallest adjacent gap that is real:        {smallest_real_gap:.1%}")

    print(
        "\nNotes: per-pair unadjusted p-values on an observed ranking "
        "(selection effects); both biases make the leaderboard look better "
        "than it is, so these noise estimates are conservative."
    )


if __name__ == "__main__":
    main()
