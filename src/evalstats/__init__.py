"""evalstats — statistical honesty for AI agent evaluations."""

from evalstats.binomial import wilson_ci
from evalstats.paired import discordant_counts, mcnemar_pvalue, paired_diff_ci
from evalstats.power import mdd_paired, needed_pairs

__version__ = "0.1.0.dev0"

__all__ = [
    "wilson_ci",
    "discordant_counts",
    "mcnemar_pvalue",
    "paired_diff_ci",
    "mdd_paired",
    "needed_pairs",
]
