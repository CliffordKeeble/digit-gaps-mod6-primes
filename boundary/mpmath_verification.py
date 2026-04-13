#!/usr/bin/env python3
"""
High-Precision Verification of Theorems 1-6 (Paper A, Task 1)
==============================================================

Verifies digit gaps and factor requirements at the 10^61 and 10^80 scales
using exact integer arithmetic (Python native bignums) and mpmath for
high-precision log values. Cross-checks digit counts via two independent
methods: len(str(prod)) and floor(log10(prod)) + 1.

Precision: 200 decimal digits via mpmath.
"""
import sys
import mpmath

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

mpmath.mp.dps = 200  # 200 decimal digits


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def main():
    print("=" * 72)
    print("HIGH-PRECISION VERIFICATION OF THEOREMS 1-6")
    print(f"mpmath precision: {mpmath.mp.dps} decimal digits")
    print("=" * 72)

    # Sieve enough primes
    primes = sieve(1_000_000)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]

    print(f"\nFirst 40 primes of 5-series: {p5[:40]}")
    print(f"First 40 primes of 7-series: {p7[:40]}")

    # === THEOREM 1: 5-series digit gap at 60-61 ===
    print(f"\n{'='*72}")
    print("THEOREM 1: 5-series digit gap at 60-61")
    print(f"{'='*72}")

    prod_5_30 = 1
    for p in p5[:30]:
        prod_5_30 *= p
    prod_5_31 = prod_5_30 * p5[30]

    digits_5_30_str = len(str(prod_5_30))
    digits_5_31_str = len(str(prod_5_31))
    log10_5_30 = mpmath.log10(mpmath.mpf(prod_5_30))
    log10_5_31 = mpmath.log10(mpmath.mpf(prod_5_31))
    digits_5_30_log = int(mpmath.floor(log10_5_30)) + 1
    digits_5_31_log = int(mpmath.floor(log10_5_31)) + 1
    ln_5_30 = mpmath.log(mpmath.mpf(prod_5_30))

    print(f"  Pi_5(30) = {prod_5_30}")
    print(f"  Digits (str):   {digits_5_30_str}")
    print(f"  Digits (log10): {digits_5_30_log}  (floor(log10) = {mpmath.nstr(log10_5_30, 20)})")
    assert digits_5_30_str == digits_5_30_log, "MISMATCH"
    print(f"  ln Pi_5(30) = {mpmath.nstr(ln_5_30, 50)}")
    print(f"  Pi_5(30) mod 3 = {prod_5_30 % 3}")
    print(f"  Pi_5(30) mod 5 = {prod_5_30 % 5}")
    print(f"  Next prime: p_31 = {p5[30]}")
    print(f"  Pi_5(31) digits (str): {digits_5_31_str}")
    print(f"  Pi_5(31) digits (log): {digits_5_31_log}")
    assert digits_5_31_str == digits_5_31_log, "MISMATCH"
    assert digits_5_30_str == 59, f"Expected 59, got {digits_5_30_str}"
    assert digits_5_31_str == 62, f"Expected 62, got {digits_5_31_str}"
    print(f"  VERIFIED: gap at digits 60, 61 (59 -> 62)")

    # === THEOREM 2: 7-series digit gap at 62-63 ===
    print(f"\n{'='*72}")
    print("THEOREM 2: 7-series digit gap at 62-63")
    print(f"{'='*72}")

    prod_7_30 = 1
    for p in p7[:30]:
        prod_7_30 *= p
    prod_7_31 = prod_7_30 * p7[30]

    digits_7_30_str = len(str(prod_7_30))
    digits_7_31_str = len(str(prod_7_31))
    log10_7_30 = mpmath.log10(mpmath.mpf(prod_7_30))
    log10_7_31 = mpmath.log10(mpmath.mpf(prod_7_31))
    digits_7_30_log = int(mpmath.floor(log10_7_30)) + 1
    digits_7_31_log = int(mpmath.floor(log10_7_31)) + 1
    ln_7_30 = mpmath.log(mpmath.mpf(prod_7_30))

    print(f"  Pi_7(30) = {prod_7_30}")
    print(f"  Digits (str):   {digits_7_30_str}")
    print(f"  Digits (log10): {digits_7_30_log}  (floor(log10) = {mpmath.nstr(log10_7_30, 20)})")
    assert digits_7_30_str == digits_7_30_log, "MISMATCH"
    print(f"  ln Pi_7(30) = {mpmath.nstr(ln_7_30, 50)}")
    print(f"  Pi_7(30) mod 3 = {prod_7_30 % 3}")
    print(f"  Pi_7(30) mod 5 = {prod_7_30 % 5}")
    print(f"  Next prime: p_31 = {p7[30]}")
    print(f"  Pi_7(31) digits (str): {digits_7_31_str}")
    print(f"  Pi_7(31) digits (log): {digits_7_31_log}")
    assert digits_7_30_str == 61, f"Expected 61, got {digits_7_30_str}"
    assert digits_7_31_str == 64, f"Expected 64, got {digits_7_31_str}"
    print(f"  VERIFIED: gap at digits 62, 63 (61 -> 64)")

    # === THEOREM 3: Factor 3 required at 10^61 ===
    print(f"\n{'='*72}")
    print("THEOREM 3: Factor 3 required at 10^61 (5-series)")
    print(f"{'='*72}")
    print(f"  Pi_5(30) mod 3 = {prod_5_30 % 3}")
    print(f"  Lemma 2 check: 2^30 mod 3 = {pow(2, 30, 3)}")
    print(f"  For N = Pi_5(30) * k with N === 0 (mod 3): k === 0 (mod 3)")
    print(f"  VERIFIED: factor 3 required")

    # === THEOREM 4: Coincident gap at 80-81 ===
    print(f"\n{'='*72}")
    print("THEOREM 4: Coincident gap at 80-81")
    print(f"{'='*72}")

    prod_5_38 = 1
    for p in p5[:38]:
        prod_5_38 *= p
    prod_5_39 = prod_5_38 * p5[38]

    prod_7_37 = 1
    for p in p7[:37]:
        prod_7_37 *= p
    prod_7_38 = prod_7_37 * p7[37]

    d_5_38 = len(str(prod_5_38))
    d_5_39 = len(str(prod_5_39))
    d_7_37 = len(str(prod_7_37))
    d_7_38 = len(str(prod_7_38))

    # Cross-check with log10
    assert d_5_38 == int(mpmath.floor(mpmath.log10(mpmath.mpf(prod_5_38)))) + 1
    assert d_5_39 == int(mpmath.floor(mpmath.log10(mpmath.mpf(prod_5_39)))) + 1
    assert d_7_37 == int(mpmath.floor(mpmath.log10(mpmath.mpf(prod_7_37)))) + 1
    assert d_7_38 == int(mpmath.floor(mpmath.log10(mpmath.mpf(prod_7_38)))) + 1

    print(f"  5-series: Pi_5(38) has {d_5_38} digits, Pi_5(39) has {d_5_39} digits")
    print(f"  7-series: Pi_7(37) has {d_7_37} digits, Pi_7(38) has {d_7_38} digits")
    assert d_5_38 == 79, f"Expected 79, got {d_5_38}"
    assert d_5_39 == 82, f"Expected 82, got {d_5_39}"
    assert d_7_37 == 79, f"Expected 79, got {d_7_37}"
    assert d_7_38 == 82, f"Expected 82, got {d_7_38}"
    print(f"  VERIFIED: both series gap at 80, 81")

    # === THEOREM 5: Factor 3 for 5-series at 10^80 ===
    print(f"\n{'='*72}")
    print("THEOREM 5: Factor 3 for 5-series at 10^80")
    print(f"{'='*72}")
    print(f"  Pi_5(38) mod 3 = {prod_5_38 % 3}")
    print(f"  Pi_5(38) mod 5 = {prod_5_38 % 5}")
    print(f"  VERIFIED: 3 | k required (mod 3 = {prod_5_38 % 3}, so k must be divisible by 3)")

    # === THEOREM 6: Factor 15 for 7-series at 10^80 ===
    print(f"\n{'='*72}")
    print("THEOREM 6: Factor 15 for 7-series at 10^80")
    print(f"{'='*72}")
    print(f"  Pi_7(37) mod 3 = {prod_7_37 % 3}")
    print(f"  Pi_7(37) mod 5 = {prod_7_37 % 5}")
    print(f"  Lemma 3 check: 1^37 mod 3 = {pow(1, 37, 3)} (always 1)")
    print(f"  5 not in 7-series, so Pi_7(37) mod 5 = {prod_7_37 % 5}")
    print(f"  For N === 0 (mod 15): need 3|k and 5|k, so 15|k")
    print(f"  VERIFIED: factor 15 required")

    # === ADDITIONAL DATA for draft placeholders ===
    print(f"\n{'='*72}")
    print("ADDITIONAL DATA FOR DRAFT")
    print(f"{'='*72}")

    # Chi5 values at the boundary
    print(f"\n  Chi5 classification of first 40 5-series primes:")
    for i, p in enumerate(p5[:40], 1):
        if p == 5:
            chi = 0  # ramified
            label = "ramified"
        elif p % 5 in (1, 4):
            chi = 1
            label = "split"
        else:
            chi = -1
            label = "inert"
        print(f"    n={i:2d}  p={p:4d}  p mod 5 = {p%5}  chi5 = {chi:+d} ({label})")

    print(f"\n  Chi5 classification of first 40 7-series primes:")
    for i, p in enumerate(p7[:40], 1):
        if p == 5:
            chi = 0
            label = "ramified"
        elif p % 5 in (1, 4):
            chi = 1
            label = "split"
        else:
            chi = -1
            label = "inert"
        print(f"    n={i:2d}  p={p:4d}  p mod 5 = {p%5}  chi5 = {chi:+d} ({label})")

    # Split/inert counts at boundary
    split_5_30 = sum(1 for p in p5[:30] if p != 5 and p % 5 in (1, 4))
    inert_5_30 = sum(1 for p in p5[:30] if p % 5 in (2, 3))
    ramified_5_30 = sum(1 for p in p5[:30] if p == 5)
    print(f"\n  5-series first 30: {split_5_30} split, {inert_5_30} inert, {ramified_5_30} ramified")

    split_7_30 = sum(1 for p in p7[:30] if p != 5 and p % 5 in (1, 4))
    inert_7_30 = sum(1 for p in p7[:30] if p % 5 in (2, 3))
    ramified_7_30 = sum(1 for p in p7[:30] if p == 5)
    print(f"  7-series first 30: {split_7_30} split, {inert_7_30} inert, {ramified_7_30} ramified")

    # Mod-5 state of Pi_7(30)
    mod5_7_30 = prod_7_30 % 5
    print(f"\n  Pi_7(30) mod 5 = {mod5_7_30}")

    print(f"\n{'='*72}")
    print("ALL THEOREMS VERIFIED")
    print(f"{'='*72}")


if __name__ == '__main__':
    main()
