#!/usr/bin/env python3
"""Task 3 (Paper 3 v3.12): §6.4 premise verification.

Hypothesis under test: small primes p ≡ 1 (mod q) for q in {4, 6, 8, 12}
have systematic over-representation of mod-5 non-residues (chi5(p) = -1).

Per CinC's Q5 refinement: exclude the ramified p=5 from each list. The
cleanest spec across all q is "first 100/1000 NON-RAMIFIED primes p ≡ 1
(mod q)". The exclusion only matters for q=4 (p=5 ≡ 1 mod 4); for q ∈
{6, 8, 12}, p=5 is not ≡ 1 mod q, so applying the filter is a no-op.

Outputs:
    For each q in {4, 6, 8, 12} and each sample size n in {100, 1000}:
        observed inerts (chi5 = -1)
        binomial two-tailed p-value against null p = 0.5
        effect size (observed - n/2) / n
    Plus a per-q summary line stating whether the bias is confirmed at
    n=1000 (p < 0.05) and in which direction.

Spot-check: brief lists primes ≡ 1 mod 4 as 5, 13, 17, 29, 37, 41, 53,
61, 73, 89 with chi5 values 0, -1, -1, +1, -1, +1, -1, +1, -1, +1.
With p=5 excluded: 13, 17, 29, 37, 41, 53, 61, 73, 89, ... → first 9
non-ramified entries with chi5: -1, -1, +1, -1, +1, -1, +1, -1, +1.
"""
import math
import os
import sys
import csv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5, binomial_two_tail_p

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

# Sieve sizing: q=12 has density 1/phi(12) = 1/4 of primes. Need 1000 such
# primes. ~4000 primes overall, the 4000th prime is ~37,800. Sieve to 200k
# for comfortable headroom.
SIEVE_LIMIT = 200_000

QS = [4, 6, 8, 12]
SAMPLE_SIZES = [100, 1000]


def first_n_primes_residue_class(primes, q, residue, n, exclude=()):
    """First n primes p with p % q == residue, excluding any in exclude."""
    out = []
    for p in primes:
        if p in exclude:
            continue
        if p % q == residue:
            out.append(p)
            if len(out) == n:
                return out
    return out


def spot_check(primes):
    """Verify the brief's hand list for q=4 (with p=5 INCLUDED, the
    non-refined version, so we can independently check our chi5 calculation
    aligns with the brief's wording)."""
    print("Spot-check vs brief's q=4 hand list (p=5 included for this check):")
    expected = [(5, 0), (13, -1), (17, -1), (29, 1), (37, -1),
                (41, 1), (53, -1), (61, 1), (73, -1), (89, 1)]
    actual = []
    count = 0
    for p in primes:
        if p % 4 == 1:
            actual.append((p, chi5(p)))
            count += 1
            if count == 10:
                break
    ok = (actual == expected)
    print(f"  expected: {expected}")
    print(f"  actual:   {actual}")
    print(f"  match: {'OK' if ok else 'FAIL'}")
    return ok


def run_q(primes, q, max_sample, exclude):
    """Pull max_sample non-ramified primes ≡ 1 mod q and tally chi5 values."""
    seq = first_n_primes_residue_class(primes, q, 1, max_sample, exclude=exclude)
    chi_vals = [chi5(p) for p in seq]
    return seq, chi_vals


def analyse_subset(chi_vals_subset):
    n = len(chi_vals_subset)
    n_inert = sum(1 for c in chi_vals_subset if c == -1)
    n_split = sum(1 for c in chi_vals_subset if c == 1)
    n_ram = sum(1 for c in chi_vals_subset if c == 0)
    p_value = binomial_two_tail_p(n_inert, n, p=0.5)
    effect = (n_inert - n / 2) / n
    return {
        'n': n, 'n_inert': n_inert, 'n_split': n_split, 'n_ramified': n_ram,
        'p_value': p_value, 'effect_size': effect,
        'fraction_inert': n_inert / n,
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    print(f"  Primes available: {len(primes)}")

    spot_ok = spot_check(primes)
    if not spot_ok:
        print("  HALT: spot-check failed.")
        sys.exit(1)
    print()

    # Per CinC Q5: exclude the ramified p=5 from all q lists.
    # (Only relevant for q=4 in practice.)
    exclude = (5,)

    rows = []
    summary_lines = []

    for q in QS:
        print(f"{'='*70}")
        print(f"q = {q}: first {max(SAMPLE_SIZES)} non-ramified primes p ≡ 1 (mod q)")
        print(f"{'='*70}")
        seq, chi_vals = run_q(primes, q, max(SAMPLE_SIZES), exclude)

        # Show first 10 for transparency
        head = list(zip(seq[:10], chi_vals[:10]))
        print(f"  first 10: {head}")

        for n in SAMPLE_SIZES:
            chi_subset = chi_vals[:n]
            res = analyse_subset(chi_subset)
            rows.append({
                'q': q, 'sample_size': n, 'n_inert': res['n_inert'],
                'n_split': res['n_split'], 'n_ramified': res['n_ramified'],
                'fraction_inert': res['fraction_inert'],
                'p_value': res['p_value'], 'effect_size': res['effect_size'],
            })
            print(f"\n  n={n}: chi5=-1 count = {res['n_inert']} "
                  f"(split=+1: {res['n_split']}, ramified=0: {res['n_ramified']})")
            print(f"    fraction inert = {res['fraction_inert']:.4f}")
            print(f"    binomial 2-tail p (null=0.5) = {res['p_value']:.6f}")
            print(f"    effect size (obs-n/2)/n = {res['effect_size']:+.4f}")

        # Summary line based on n=1000 result
        r1000 = next(r for r in rows if r['q'] == q and r['sample_size'] == 1000)
        if r1000['p_value'] < 0.05:
            direction = "EXCESS chi5=-1 (over-representation of inerts)" \
                if r1000['effect_size'] > 0 \
                else "DEFICIT chi5=-1 (over-representation of splits)"
            confirmed = "CONFIRMED"
        else:
            direction = "no significant bias"
            confirmed = "NOT CONFIRMED"
        line = (f"q={q}: at n=1000 the bias is {confirmed} (p={r1000['p_value']:.4f}); "
                f"direction = {direction}")
        summary_lines.append(line)
        print(f"\n  -> {line}")
        print()

    # Save CSV
    csv_path = os.path.join(RESULTS_DIR, 'task3_premise.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['q', 'sample_size', 'n_inert', 'n_split', 'n_ramified',
                    'fraction_inert', 'p_value', 'effect_size'])
        for r in rows:
            w.writerow([r['q'], r['sample_size'], r['n_inert'], r['n_split'],
                        r['n_ramified'], f"{r['fraction_inert']:.6f}",
                        f"{r['p_value']:.6f}", f"{r['effect_size']:.6f}"])
    print(f"Saved: {csv_path}")

    # Per-q summary at end
    print(f"\n{'='*70}")
    print("Summary (n=1000 results):")
    print(f"{'='*70}")
    for line in summary_lines:
        print(f"  {line}")


if __name__ == '__main__':
    main()
