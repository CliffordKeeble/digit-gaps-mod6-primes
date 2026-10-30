# Independent implementation (numpy). Written from the papers' definitions, not from the repo's code,
# except the cluster-detection rule, which is transcribed from full_null_model.py so the same object is measured.
# (Ported from the 7 October 2026 review's core.py, unchanged in what it computes.)
import math

import numpy as np


def primes_upto(n):
    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = False
    return np.flatnonzero(sieve)


def cumlog10(primes):
    # long double cumulative sum of log10(p)
    return np.cumsum(np.log10(primes.astype(np.longdouble)))


def gap_arrays(L1, L2):
    digits1 = np.floor(L1).astype(np.int64) + 1
    digits2 = np.floor(L2).astype(np.int64) + 1
    max_digits = int(min(digits1.max(), digits2.max()))
    gaps1 = np.ones(max_digits + 1, dtype=bool)
    gaps2 = np.ones(max_digits + 1, dtype=bool)
    gaps1[digits1[digits1 <= max_digits]] = False
    gaps2[digits2[digits2 <= max_digits]] = False
    gaps1[0] = gaps2[0] = False
    return gaps1, gaps2, max_digits


def find_clusters(
    gaps1, gaps2, max_digits, window=50, min_gaps=20, merge_dist=500, step=10
):
    # same rule as full_null_model.find_clusters_fast, vectorised
    both = (gaps1 & gaps2).astype(np.int64)
    any_gap = (gaps1 | gaps2).astype(np.int64)
    cumulative_both = np.concatenate(([0], np.cumsum(both)))
    cumulative_any = np.concatenate(([0], np.cumsum(any_gap)))
    starts = np.arange(1, max_digits - window + 1, step)
    starts = starts[starts + window <= max_digits]
    count_both = cumulative_both[starts + window] - cumulative_both[starts]
    count_any = cumulative_any[starts + window] - cumulative_any[starts]
    sync = starts[(count_any >= min_gaps) & (count_both == count_any)]
    if len(sync) == 0:
        return []
    clusters = []
    low = int(sync[0])
    high = low + window
    for start in sync[1:]:
        start = int(start)
        if start <= high + merge_dist:
            high = start + window
        else:
            clusters.append(((low + high) // 2, high - low, low, high))
            low, high = start, start + window
    clusters.append(((low + high) // 2, high - low, low, high))
    return clusters


def fit_power_law(centres):
    centre_array = np.asarray(centres, dtype=float)
    if len(centre_array) < 4:
        return None
    spacings = np.diff(centre_array)
    midpoints = (centre_array[:-1] + centre_array[1:]) / 2
    usable = (spacings > 0) & (midpoints > 0)
    x = np.log(midpoints[usable])
    y = np.log(spacings[usable])
    n = len(x)
    if n < 3:
        return None
    mean_x, mean_y = x.mean(), y.mean()
    sum_xx = ((x - mean_x) ** 2).sum()
    if sum_xx == 0:
        return None
    beta = ((x - mean_x) * (y - mean_y)).sum() / sum_xx
    intercept = mean_y - beta * mean_x
    residual = ((y - (intercept + beta * x)) ** 2).sum()
    total = ((y - mean_y) ** 2).sum()
    r2 = 1 - residual / total if total > 0 else 0.0
    se = math.sqrt(residual / ((n - 2) * sum_xx)) if n > 2 else float("nan")
    return {"beta": beta, "r2": r2, "se": se, "n": n, "A": math.exp(intercept)}
