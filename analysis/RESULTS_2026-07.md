# SWE-bench Verified noise re-analysis — snapshot 2026-07-01

Data: per-instance `results/results.json` from the public
[SWE-bench/experiments](https://github.com/SWE-bench/experiments) repo,
`evaluation/verified/`, fetched 2026-07-01 (134 submissions, 2023-10 → 2025-12).
Reproduce with:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/SWE-bench/experiments.git
cd experiments && git sparse-checkout set --no-cone '/evaluation/verified/*/results/results.json'
python analysis/swebench_noise.py --experiments-dir ./experiments
```

(A copy of the 134 results.json files as fetched lives in `data/swebench-experiments/`,
gitignored; the numbers below are reproducible from either source.)

## Headline findings

1. **The #1 spot is literally a coin flip.** The top two submissions
   (79.2% vs 79.2%) differ on 36 instances — 18 wins each way. Exact
   McNemar p = 1.0.

2. **97% of adjacent leaderboard pairs are statistically
   indistinguishable** (129/133 at p ≥ 0.05, exact McNemar on discordant
   pairs). The visual ordering of the leaderboard is almost entirely noise
   at adjacent ranks.

3. **76% of all pairs within 5 points of each other are
   indistinguishable** (1,076/1,419 pairs).

4. **The benchmark's minimal detectable difference is ~5.4 points.**
   Median adjacent-pair discordance is 18.4%; at N=500 and 80% power the
   smallest reliably-detectable true difference is 5.4 percentage points.
   Corollary: to certify a 2-point improvement at this discordance you
   need ~3,600 tasks — 7x the benchmark's size.

5. **Gaps up to 3.4 points appear as noise** in adjacent pairs; the
   smallest adjacent gap that does reach significance is 2.6 points (a
   low-discordance pair). Any marketing claim built on a lead smaller than
   ~4-5 points is unfalsifiable at this N.

6. Single-system Wilson CIs at the top span roughly ±3.7 points — wider
   than most of the gaps the leaderboard's ordering implies.

## Caveats (also printed by the script)

- Adjacent-rank comparisons on an observed ranking involve selection
  effects (order statistics), and per-pair p-values are unadjusted for
  multiple comparisons. **Both biases flatter the leaderboard**, so the
  noise fractions above are conservative.
- Paired tests assume all submissions ran the same 500 instances; the
  loader warns on any submission whose resolved set exceeds the split.

## Candidate follow-ups

- Same analysis for SWE-bench Lite (N=300 — MDD will be worse).
- Scaffold-vs-model decomposition: several top-5 entries share a base
  model with different scaffolds and are pairwise noise — is the model the
  real variable? (Needs care: submissions vary in more than one way.)
- Time-series: has the top-of-leaderboard discordance shrunk as scores
  saturate? (Saturation compresses discordance and makes ranking noise
  *worse*.)
