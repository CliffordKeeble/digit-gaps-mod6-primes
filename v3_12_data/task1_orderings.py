#!/usr/bin/env python3
"""Task 1 (Paper 3 v3.12): Structured-ordering controls for §6.5.1.

For each window n in {20, 33, 50, 70, 90, 100} and each definition (A, C):
    A: include the ramified p=5 at position 1 (n-step running sum)
    C: omit the ramified p=5 (n-1 step running sum, primary)
test the chi5 tie count under each of:
    1. Natural             — 5-series primes by ascending size (baseline)
    2. Reversed-size       — same multiset, descending order
    3. Every-other-prime   — odd-indexed then even-indexed (1-indexed)
    4. Index-interleaved   — first half and second half alternated
    5. Chi-clustered       — all chi=+1 then all chi=-1 (deterministic
                              minimum-tie lower-bound control)
    6. Random shuffle      — 1000 trials with seed = trial * 137 + 42

Brief change vs spec: Reversed-sequence (#3 in brief) was identified as
operationally identical to Reversed-size on a size-ordered prime set, so
dropped per CinC's confirmation. Chi-clustered added as optional sixth
ordering for symmetric coverage.

Verification gates (halt if not matched):
    Def C, n=33, natural:     T=13, shuf_mean ≈ 6.17, z ≈ 2.45
    Def A, n=90, natural:     T=29, z ≈ 3.64
"""
import math
import os
import random
import csv
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5, five_series_primes

SIEVE_LIMIT = 2_000_000
N_SHUFFLE = 1000
WINDOWS = [20, 33, 50, 70, 90, 100]

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


# ---------------------------------------------------------------------------
# Orderings — each returns a permutation (list of 0-based indices) of length L
# ---------------------------------------------------------------------------

def order_natural(L):
    return list(range(L))


def order_reversed_size(L):
    return list(range(L - 1, -1, -1))


def order_every_other(L):
    """1-indexed odds then 1-indexed evens, converted to 0-based.

    Spec: '{1, 3, 5, ...} concatenated with {2, 4, 6, ...}'
    1-indexed odds = positions 1, 3, 5, ... → 0-based 0, 2, 4, ...
    1-indexed evens = positions 2, 4, 6, ... → 0-based 1, 3, 5, ...
    """
    odds_zero_based = list(range(0, L, 2))
    evens_zero_based = list(range(1, L, 2))
    return odds_zero_based + evens_zero_based


def order_index_interleaved(L):
    """Two halves of natural sequence alternated.

    Halve into first half [0..h-1] and second half [h..L-1] with
    h = ceil(L/2). Then interleave: first_half[0], second_half[0],
    first_half[1], second_half[1], ...
    For odd L the first half is one longer than the second.
    """
    h = (L + 1) // 2
    first = list(range(h))
    second = list(range(h, L))
    out = []
    i = 0
    while i < len(first) or i < len(second):
        if i < len(first):
            out.append(first[i])
        if i < len(second):
            out.append(second[i])
        i += 1
    return out


def order_chi_clustered(chi_seq):
    """All chi=+1 indices first (in natural order), then chi=-1 (natural),
    then chi=0 (natural). Deterministic minimum-tie ordering by construction:
    a single up-ramp then a single down-ramp, so the only tie is the
    inevitable one when the ramp returns to zero (or none if the multiset
    is unbalanced). Lower-bound control."""
    plus = [i for i, c in enumerate(chi_seq) if c == 1]
    minus = [i for i, c in enumerate(chi_seq) if c == -1]
    zeros = [i for i, c in enumerate(chi_seq) if c == 0]
    return plus + minus + zeros


# ---------------------------------------------------------------------------
# Tie counting
# ---------------------------------------------------------------------------

def tie_count(chi_seq, perm):
    """Count positions k where the running sum of chi_seq[perm[0..k]] is 0."""
    s = 0
    ties = 0
    for idx in perm:
        s += chi_seq[idx]
        if s == 0:
            ties += 1
    return ties


def shuffle_baseline(chi_seq, n_trials=N_SHUFFLE):
    """1000 shuffles with seed = trial * 137 + 42 per the v3.11 scheme."""
    counts = []
    for trial in range(n_trials):
        rng = random.Random(trial * 137 + 42)
        perm = list(range(len(chi_seq)))
        rng.shuffle(perm)
        counts.append(tie_count(chi_seq, perm))
    return counts


def stats(counts):
    """Mean, sample std, n_distinct."""
    n = len(counts)
    mean = sum(counts) / n
    if n > 1:
        std = math.sqrt(sum((x - mean) ** 2 for x in counts) / (n - 1))
    else:
        std = 0.0
    return mean, std, len(set(counts))


def z_and_p(T, shuffle_counts):
    mean, std, _ = stats(shuffle_counts)
    z = (T - mean) / std if std > 0 else 0.0
    p_ge = sum(1 for x in shuffle_counts if x >= T) / len(shuffle_counts)
    return z, p_ge, mean, std


# ---------------------------------------------------------------------------
# Definition-specific chi sequences
# ---------------------------------------------------------------------------

def chi_seq_def_A(p5, n):
    """Def A at window n: chi values for first n 5-series primes (incl p=5)."""
    return [chi5(p) for p in p5[:n]]


def chi_seq_def_C(p5, n):
    """Def C at window n: drop the ramified p=5; (n-1) chi values."""
    return [chi5(p) for p in p5[1:n]]


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

ORDERINGS = [
    ('natural', order_natural),
    ('reversed_size', order_reversed_size),
    ('every_other', order_every_other),
    ('index_interleaved', order_index_interleaved),
    ('chi_clustered', order_chi_clustered),
]


def run_definition(p5, def_label, chi_builder):
    """For one definition, sweep all windows and orderings."""
    print(f"\n{'='*78}")
    print(f"Definition {def_label}")
    print(f"{'='*78}")

    rows = []
    for n in WINDOWS:
        chi_seq = chi_builder(p5, n)
        L = len(chi_seq)

        # Build the shuffle baseline once per (definition, window).
        shuf_counts = shuffle_baseline(chi_seq)
        shuf_mean, shuf_std, n_distinct = stats(shuf_counts)

        print(f"\n  n={n}  (chi sequence length L={L}, shuf_mean={shuf_mean:.3f}, "
              f"shuf_std={shuf_std:.3f}, n_distinct={n_distinct})")
        print(f"  {'ordering':>20}  {'T':>4}  {'z':>7}  {'p_ge':>7}")
        print(f"  {'-'*48}")

        for name, fn in ORDERINGS:
            if name == 'chi_clustered':
                perm = fn(chi_seq)
            else:
                perm = fn(L)
            T = tie_count(chi_seq, perm)
            z, p_ge, _, _ = z_and_p(T, shuf_counts)
            rows.append({
                'definition': def_label,
                'n_window': n,
                'L_effective': L,
                'ordering': name,
                'T': T,
                'shuffle_mean': shuf_mean,
                'shuffle_std': shuf_std,
                'shuffle_n_distinct': n_distinct,
                'z': z,
                'p_ge': p_ge,
            })
            print(f"  {name:>20}  {T:>4}  {z:>7.2f}  {p_ge:>7.4f}")

        # Append the random-shuffle baseline summary as its own row for visibility
        rows.append({
            'definition': def_label,
            'n_window': n,
            'L_effective': L,
            'ordering': 'random_shuffle_baseline',
            'T': None,
            'shuffle_mean': shuf_mean,
            'shuffle_std': shuf_std,
            'shuffle_n_distinct': n_distinct,
            'z': 0.0,
            'p_ge': None,
        })
    return rows


def write_csv(rows, path):
    fields = ['definition', 'n_window', 'L_effective', 'ordering',
              'T', 'shuffle_mean', 'shuffle_std', 'shuffle_n_distinct',
              'z', 'p_ge']
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(fields)
        for r in rows:
            row_out = []
            for k in fields:
                v = r.get(k)
                if v is None:
                    row_out.append('')
                elif isinstance(v, float):
                    row_out.append(f"{v:.6f}")
                else:
                    row_out.append(v)
            w.writerow(row_out)


def verify_anchors(rows_a, rows_c):
    """Halt if the v3.11 anchors don't reproduce."""
    print(f"\n{'='*78}")
    print("Verification against v3.11 anchors")
    print(f"{'='*78}")

    def find(rows, definition, n, ordering):
        for r in rows:
            if (r['definition'] == definition and r['n_window'] == n
                    and r['ordering'] == ordering):
                return r
        return None

    fail = False

    r_c = find(rows_c, 'C', 33, 'natural')
    print(f"\n  Def C, n=33, natural: T={r_c['T']}, shuf_mean={r_c['shuffle_mean']:.3f}, "
          f"shuf_std={r_c['shuffle_std']:.3f}, z={r_c['z']:.3f}")
    print(f"    Expected: T=13, shuf_mean ≈ 6.17, z ≈ 2.45")
    if r_c['T'] != 13:
        print("    FAIL: T mismatch")
        fail = True
    if abs(r_c['shuffle_mean'] - 6.17) > 0.30:
        print(f"    FAIL: shuf_mean off by > 0.30 (got {r_c['shuffle_mean']:.3f})")
        fail = True
    if abs(r_c['z'] - 2.45) > 0.30:
        print(f"    FAIL: z off by > 0.30 (got {r_c['z']:.3f})")
        fail = True

    r_a = find(rows_a, 'A', 90, 'natural')
    print(f"\n  Def A, n=90, natural: T={r_a['T']}, z={r_a['z']:.3f}")
    print(f"    Expected: T=29, z ≈ 3.64")
    if r_a['T'] != 29:
        print("    FAIL: T mismatch")
        fail = True
    if abs(r_a['z'] - 3.64) > 0.40:
        print(f"    FAIL: z off by > 0.40 (got {r_a['z']:.3f})")
        fail = True

    if fail:
        print("\n  HALT: verification failed. Reporting before extending.")
        sys.exit(1)
    else:
        print("\n  OK: anchors reproduce within tolerance.")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = five_series_primes(primes)
    print(f"  5-series primes available: {len(p5)} (first: {p5[:6]})")

    rows_a = run_definition(p5, 'A', chi_seq_def_A)
    rows_c = run_definition(p5, 'C', chi_seq_def_C)

    csv_a = os.path.join(RESULTS_DIR, 'task1_orderings_def_A.csv')
    csv_c = os.path.join(RESULTS_DIR, 'task1_orderings_def_C.csv')
    write_csv(rows_a, csv_a)
    write_csv(rows_c, csv_c)
    print(f"\nSaved: {csv_a}")
    print(f"Saved: {csv_c}")

    verify_anchors(rows_a, rows_c)

    # Compact summary
    print(f"\n{'='*78}")
    print("Compact summary — z-score by ordering and window")
    print(f"{'='*78}")
    for def_label, rows in [('A', rows_a), ('C', rows_c)]:
        print(f"\n  Definition {def_label}:")
        header = f"  {'ordering':>20}  " + "  ".join(f"n={n:<3}" for n in WINDOWS)
        print(header)
        for ordering_name, _ in ORDERINGS:
            cells = []
            for n in WINDOWS:
                r = next((r for r in rows if r['n_window'] == n
                          and r['ordering'] == ordering_name), None)
                cells.append(f"{r['z']:>5.2f}")
            print(f"  {ordering_name:>20}  " + "  ".join(cells))


if __name__ == '__main__':
    main()
