# evalstats

**Statistical honesty for AI agent evaluations.**

Agent benchmarks are expensive, low-N, and high-variance — and most published
"improvements" are reported without error bars. `evalstats` provides the
statistical machinery that agent-eval reports usually skip:

- **Confidence intervals** for success rates (Wilson, not Wald)
- **Paired comparisons** for two systems on the same task set
  (McNemar exact test, paired-difference CIs) — the correct test for
  leaderboard deltas, and far more sensitive than comparing two marginal
  scores
- **Power analysis / minimal detectable difference** — "how big a gap can
  this benchmark actually resolve at N tasks?"
- *(roadmap)* hierarchical CIs for task × run × scaffold variance,
  sequential early-stopping tests for expensive eval runs, variance
  decomposition

## Install

```bash
pip install git+https://github.com/tapishr/evalstats
```

(Pre-1.0; install from source. PyPI package to follow once the API settles.)

## Quickstart

```python
from evalstats import wilson_ci, discordant_counts, mcnemar_pvalue, paired_diff_ci, mdd_paired

# A single system: 292/500 tasks solved
lo, hi = wilson_ci(292, 500)            # -> (0.541, 0.626)

# Two systems on the SAME 500 tasks (paired — the right way)
b, c = discordant_counts(resolved_a, resolved_b)   # A-only wins, B-only wins
p = mcnemar_pvalue(b, c)                           # exact test on discordant pairs
diff, lo, hi = paired_diff_ci(b, c, n=500)         # CI on the score difference

# What difference can this benchmark even detect?
mdd_paired(n=500, discordance=0.20)     # -> ~0.056 (5.6 points!) at 80% power
```

## The essay

**[The #1 Spot on SWE-bench Is a Coin Flip](ESSAY.md)** — the launch write-up. The top two
systems on SWE-bench Verified are tied at 79.2%, disagree on 36 tasks, and split them 18–18.
97% of adjacent leaderboard pairs are statistically indistinguishable.

## The point

At N=500 tasks (SWE-bench Verified) with typical between-system discordance,
differences smaller than **~4–6 percentage points are statistically
indistinguishable** in a paired design — and marginal (unpaired) comparisons
are weaker still. A large fraction of adjacent leaderboard placements are
therefore noise. See `analysis/swebench_noise.py` for the reproducible
re-analysis of public per-instance leaderboard data.

## Status

Pre-0.1, under active development (July 2026). API may move.

## License

MIT
