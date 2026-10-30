"""The 13 synchronisation clusters, found, not typed.

Primes to 1.5e7, the cumulative log10 products of the two series, the digit
gaps, and the cluster finder (core.py). Writes work/cluster_centres.npy for
fig_beat.py, and prints the centres beside those in the 7 October log
(data/reference_step1_reproduce.log), which they should agree with.
"""

import re
import time

import numpy as np
from common import DATA, WORK, Log, describe_longdouble
from core import (
    cumlog10,
    find_clusters,
    fit_power_law,
    gap_arrays,
    primes_upto,
)

PRIME_BOUND = 15_000_000
CLUSTER_RANGE = 200_000


def reference_centres():
    pattern = re.compile(r"^\s+centre\s+(\d+)\s+span\s+(\d+)\s+\[(\d+), (\d+)\]\s*$")
    found = []
    for line in (DATA / "reference_step1_reproduce.log").read_text().splitlines():
        match = pattern.match(line)
        if match:
            found.append(tuple(int(group) for group in match.groups()))
    return found


def main():
    with Log("step1_clusters") as log:
        start_time = time.time()
        log(describe_longdouble())
        primes = primes_upto(PRIME_BOUND)
        series_5 = primes[(primes > 3) & (primes % 6 == 5)]
        series_7 = primes[(primes > 3) & (primes % 6 == 1)]
        log(
            f"primes<=15e6: {len(primes)}  5-series: {len(series_5)}"
            f"  7-series: {len(series_7)}"
        )
        n_use = min(len(series_5), len(series_7))
        log5 = cumlog10(series_5[:n_use])
        log7 = cumlog10(series_7[:n_use])
        gaps_5, gaps_7, max_digits = gap_arrays(log5, log7)
        log(f"max digit-length (min of the two series): {max_digits}")
        coincident = np.flatnonzero(gaps_5 & gaps_7)
        log(
            f"gaps 5-series: {gaps_5.sum()} ({100 * gaps_5.sum() / max_digits:.2f}%)"
            f"  7-series: {gaps_7.sum()} ({100 * gaps_7.sum() / max_digits:.2f}%)"
            f"  coincident: {len(coincident)} ({100 * len(coincident) / max_digits:.2f}%)"
        )

        clusters = find_clusters(gaps_5, gaps_7, min(CLUSTER_RANGE, max_digits))
        fit = fit_power_law([cluster[0] for cluster in clusters])
        log(
            f"clusters to {CLUSTER_RANGE}: {len(clusters)} ; fit: "
            + (
                str(
                    {
                        key: (value if key == "n" else round(float(value), 4))
                        for key, value in fit.items()
                    }
                )
                if fit
                else "None"
            )
        )
        for centre, span, low, high in clusters:
            log(f"   centre {centre:7d}  span {span:5d}  [{low}, {high}]")

        WORK.mkdir(exist_ok=True)
        np.save(WORK / "cluster_centres.npy", np.array([c[0] for c in clusters]))

        reference = reference_centres()
        computed = [tuple(int(value) for value in cluster) for cluster in clusters]
        agree = computed == reference
        log(
            f"\nagainst the 7 October log ({len(reference)} clusters, Linux): "
            + ("all 13 centres, spans and edges AGREE" if agree else "DISAGREE")
        )
        if not agree:
            log("   computed here / 7 October log, where they differ:")
            for here, there in zip(computed, reference, strict=False):
                if here != there:
                    log(f"   {here} / {there}")
        log(f"elapsed {time.time() - start_time:.1f} s")


if __name__ == "__main__":
    main()
