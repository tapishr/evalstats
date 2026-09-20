# The #1 Spot on SWE-bench Is a Coin Flip

The two best coding agents on SWE-bench Verified — the benchmark the field treats as the scoreboard for AI software engineering — are tied at 79.2%. Each solves 396 of the same 500 tasks.

That's not the interesting part. The interesting part is *which* 396. They don't agree on the same 396. On 36 of the tasks, exactly one of the two succeeds — and it's an even split: 18 tasks where the first agent wins, 18 where the second does. Eighteen to eighteen.

If you handed those 36 disagreements to a referee who had to decide which agent is better, the honest answer is the one you'd get from flipping a coin 36 times and finding it came up 18 heads. Which is to say: there is no answer. The number-one and number-two systems on the most-watched agent benchmark in the world are, statistically, indistinguishable. The ranking that puts one above the other is reporting noise as if it were signal.

I checked whether this is a fluke of the top two. It isn't. It's the leaderboard.

## What "the leaderboard is noise" actually means

Take every pair of adjacent entries in the Verified ranking — #1 vs #2, #2 vs #3, and so on down. For each pair, ask the only question that matters: is the gap between them larger than what you'd expect from chance, given that the benchmark is only 500 tasks?

**129 of 133 adjacent pairs — 97% — are statistically indistinguishable.** Not "close." Indistinguishable: the difference between them fails a significance test at the standard threshold. Widen the net to every pair of systems within five points of each other, and **76% of those pairs are indistinguishable too** (1,076 of 1,419).

The benchmark's resolving power tells you why. With 500 tasks and the amount two similar agents typically disagree, the smallest true difference SWE-bench Verified can reliably detect is about **5.4 percentage points.** Anything smaller than that is below the noise floor. Most of the leaderboard's gaps are smaller than that. So most of the leaderboard's ordering is unfalsifiable — it's showing you a rank order that the data cannot actually support.

A concrete illustration of how thoroughly rank-distance and real-difference have come apart: the largest adjacent gap that still reads as noise is 3.4 points, while the smallest adjacent gap that reaches significance is 2.6 points. A 2.6-point gap can be real and a 3.4-point gap can be noise, because significance depends on *how much the two systems disagree*, not on how far apart the leaderboard prints them. The ranking is sorting on a number that doesn't mean what the ranking implies it means.

## The method, honestly and briefly

Three sentences, because you should be able to check my reasoning, not just my result.

When two systems run the *same* 500 tasks, the tasks where they both succeed or both fail tell you nothing about which is better — only the tasks where exactly one succeeds (the *discordant* pairs) carry a signal, and the right test is the exact **McNemar test**, which asks whether that split is distinguishable from a coin flip. This is a stricter and more honest comparison than putting two overall percentages side by side, because two agents can post very different scores while disagreeing on almost nothing, or nearly identical scores while disagreeing constantly — and only the disagreement is evidence. The "minimal detectable difference" of 5.4 points is a standard power calculation: given the observed disagreement rate and 500 tasks, it's the smallest true gap you could catch 80% of the time.

None of this is exotic. It's the statistics you'd be required to report in any empirical field that adopted error bars. Agent benchmarking simply hasn't adopted them yet.

## The caveats, up front, because they cut toward me

I want to be the first to list the ways this analysis could be too harsh, because there aren't many and they don't rescue the leaderboard — they make the picture *worse*.

**Multiple comparisons.** I ran a significance test on every adjacent pair without correcting for the fact that I ran many tests. Correcting would only find *more* pairs indistinguishable, not fewer. The uncorrected version is the charitable one.

**Selection effects.** Comparing entries *because* they landed next to each other on an observed ranking is comparing order statistics, which are biased toward looking more different than the underlying systems are. Accounting for it would, again, push toward more noise, not less.

**Same-instance assumption.** The paired tests assume every submission ran the identical 500 instances. Where a submission reports a different task set, that would add noise to the comparison — not remove it.

Every direction the caveats point is the same direction: **the real leaderboard is noisier than what I'm showing you.** This is the opposite of the usual situation, where an author's caveats are the load-bearing defense against their headline. Here the headline is the conservative claim.

## "Everyone knows benchmarks are noisy"

This is the response I expect, and it's worth answering directly, because it's half right.

Yes — if you ask any experienced researcher whether SWE-bench rankings are noisy, they'll say of course. The intuition is common. But an intuition that "of course it's noisy" is not the same as knowing that the #1 spot is a literal coin flip, that 97% of adjacent rankings fail a significance test, and that the benchmark can't resolve anything under 5.4 points. Those are specific, quantified, checkable facts, and until you compute them, "it's noisy" is a shrug that lets everyone keep citing the ranking anyway — in launch posts, in fundraising decks, in procurement decisions, in press coverage that reports a two-point lead as a breakthrough.

The gap between "people vaguely know" and "here is the number, here is the code, check it yourself" is the entire contribution. Vibes don't change behavior. A reproducible coin flip might.

## Check it yourself in ten minutes

This whole analysis runs on data the submissions already publish. Every entry in the [SWE-bench experiments repository](https://github.com/SWE-bench/experiments) includes a per-instance results file — which of the 500 tasks it solved. No agent was re-run. No compute was spent. It's arithmetic on public data.

I packaged the statistics as a small open-source library:

```
pip install git+https://github.com/tapishr/evalstats
```

It gives you Wilson confidence intervals for a single system, the exact McNemar test and paired-difference intervals for comparing two, and the power calculation that produces the minimal-detectable-difference number. The [analysis script](https://github.com/tapishr/evalstats/blob/main/analysis/swebench_noise.py) reproduces every figure in this post from the public data.

And if you'd rather just feel it than run it: I built an [interactive widget](https://tapishr.github.io/evalstats/widget/) — pick any two SWE-bench submissions from the dropdowns and it shows you the discordant split, the p-value, and whether the gap survives. Start with the default pair. Watch the #1 and #2 systems come up as a coin flip. Then try to find a pair in the top ten that *isn't*.

## What to do instead

The point of this isn't to dunk on SWE-bench, which was a genuine contribution and moved the field forward, or on the teams who submit to it, most of whom privately know the benchmark is saturating. The point is that the *way we read the leaderboard* has outrun what the leaderboard can support, and three changes fix it.

**Report confidence intervals, not point scores.** A system that solves 79.2% of 500 tasks has a 95% interval spanning just over seven points — from about 75% to 82%. If your leaderboard printed the intervals, the top dozen systems would visibly overlap into a single band, and no one would write "state of the art by two points" with a straight face. Error bars are not a nicety here; they are the difference between a measurement and a number.

**Compare systems paired, not marginal.** When two systems ran the same tasks, don't put their two percentages side by side — run the McNemar test on their disagreements. It's more sensitive and it's correct. The tools to do it are now one `pip install` away.

**Design benchmarks for the differences you want to detect.** If the field wants to distinguish systems that differ by two points — and at current saturation, two points is a typical "improvement" — a 500-task benchmark cannot do it. Detecting a reliable two-point difference at this disagreement rate needs roughly 3,600 tasks, about seven times Verified's size. Either the benchmarks get much larger, or we stop pretending two-point gaps mean anything. Both are fine. Reporting two-point gaps as breakthroughs on a 500-task set is not.

The uncomfortable version of all this: for the last year, a meaningful share of "new state of the art on SWE-bench" announcements have been reporting movement within the noise band. Not because anyone was dishonest — because the benchmark shipped without error bars and everyone read the ranking literally. The fix is cheap. It's four lines of statistics and the willingness to show the interval.

I'd rather the field adopt the four lines.

---

*evalstats is MIT-licensed and pre-1.0; the SWE-bench analysis, the widget, and the reproduction instructions are in the repo. If you find an error in the method, tell me — the entire point is that it's checkable, and a corrected coin flip is still a coin flip.*

---

*Published 20 September 2026. Every figure reproduces from public data with `python analysis/swebench_noise.py --experiments-dir <clone of SWE-bench/experiments>`; re-verified against the live leaderboard the morning of publication.*
