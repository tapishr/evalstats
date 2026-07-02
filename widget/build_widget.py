#!/usr/bin/env python3
"""Build the standalone SWE-bench 'is that gap real?' widget.

Reads the per-instance results.json files, packs each submission's resolved
set into a base64 bitmask over the union of all resolved instance IDs, computes
the aggregate headline numbers, and injects everything into template.html to
produce a single self-contained index.html (no external requests, no CDN).

Usage:
    python widget/build_widget.py [--data-dir data/swebench-experiments] [--split verified]
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from evalstats import discordant_counts, mcnemar_pvalue, mdd_paired  # noqa: E402

SPLIT_SIZES = {"verified": 500, "lite": 300, "test": 2294}


def load(data_dir: Path, split: str) -> dict[str, set[str]]:
    split_dir = data_dir / "evaluation" / split
    out: dict[str, set[str]] = {}
    for sub in sorted(split_dir.iterdir()):
        rf = sub / "results" / "results.json"
        if not rf.is_file():
            continue
        try:
            resolved = json.loads(rf.read_text()).get("resolved")
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(resolved, list):
            out[sub.name] = set(resolved)
    return out


def pack_bits(resolved: set[str], order: dict[str, int], n_bytes: int) -> str:
    buf = bytearray(n_bytes)
    for inst in resolved:
        idx = order.get(inst)
        if idx is not None:
            buf[idx >> 3] |= 1 << (idx & 7)
    return base64.b64encode(bytes(buf)).decode()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=ROOT / "data" / "swebench-experiments")
    ap.add_argument("--split", default="verified", choices=SPLIT_SIZES)
    ap.add_argument("--snapshot", default="2026-07-01")
    args = ap.parse_args()

    n_total = SPLIT_SIZES[args.split]
    subs = load(args.data_dir, args.split)
    if len(subs) < 2:
        raise SystemExit(f"need >=2 submissions, found {len(subs)} in {args.data_dir}")

    # canonical bit order = sorted union of all resolved instances
    universe = sorted(set().union(*subs.values()))
    order = {inst: i for i, inst in enumerate(universe)}
    n_bytes = (len(universe) + 7) // 8

    packed = [
        {"name": name, "k": len(resolved), "b": pack_bits(resolved, order, n_bytes)}
        for name, resolved in subs.items()
    ]

    # aggregates (mirror analysis/swebench_noise.py)
    ranked = sorted(subs.items(), key=lambda kv: len(kv[1]), reverse=True)
    adj = list(zip(ranked, ranked[1:]))
    adj_noise = sum(
        1 for (na, ra), (nb, rb) in adj
        if mcnemar_pvalue(*discordant_counts(ra, rb)) >= 0.05
    )
    near_total = near_noise = 0
    for i, (na, ra) in enumerate(ranked):
        for nb, rb in ranked[i + 1:]:
            if (len(ra) - len(rb)) / n_total > 0.05:
                break
            near_total += 1
            if mcnemar_pvalue(*discordant_counts(ra, rb)) >= 0.05:
                near_noise += 1
    disc = sorted((sum(discordant_counts(ra, rb)) / n_total) for (na, ra), (nb, rb) in adj)
    med_disc = disc[len(disc) // 2]

    agg = {
        "adj_noise_pct": round(100 * adj_noise / len(adj)),
        "near_noise_pct": round(100 * near_noise / near_total) if near_total else 0,
        "mdd_pts": round(100 * mdd_paired(n_total, med_disc), 1),
    }

    blob = {"n": n_total, "subs": packed, "agg": agg}
    template = (Path(__file__).parent / "template.html").read_text()
    html = template.replace("__DATA__", json.dumps(blob, separators=(",", ":"))) \
                   .replace("__SNAPSHOT__", args.snapshot)

    out = Path(__file__).parent / "index.html"
    out.write_text(html)
    kb = len(html.encode()) / 1024
    print(f"wrote {out} ({kb:.0f} KB, {len(packed)} submissions, {len(universe)} instances in universe)")
    print(f"aggregates: {agg}")


if __name__ == "__main__":
    main()
