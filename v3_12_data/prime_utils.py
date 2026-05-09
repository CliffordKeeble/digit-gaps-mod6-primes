#!/usr/bin/env python3
"""Shared prime utilities for Paper 3 v3.12 data generation.

Convention (matching the existing repo, e.g. boundary/shuffle_robustness.py):
- 5-series primes: p > 3 with p % 6 == 5 (this includes the ramified p=5).
- chi5(p) = Legendre symbol (p / 5): +1 if p in {1,4} mod 5, -1 if p in {2,3} mod 5, 0 if p == 5.
"""
import math


def sieve(limit):
    """Sieve of Eratosthenes up to limit (inclusive). Returns list of primes."""
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def chi5(p):
    """Legendre symbol (p / 5). Returns +1, -1, or 0 (ramified at p=5)."""
    r = p % 5
    if r == 0:
        return 0
    elif r in (1, 4):
        return 1
    else:
        return -1


def five_series_primes(primes):
    """5-series primes per repo convention: p > 3 and p % 6 == 5.

    The ramified p=5 satisfies these (5 > 3 and 5 % 6 == 5), so it is the
    first 5-series prime. The next are 11, 17, 23, 29, 41, ...
    """
    return [p for p in primes if p > 3 and p % 6 == 5]


def t_pvalue_twotail(t_stat, df):
    """Two-tailed p-value for a t-statistic with df degrees of freedom.

    Uses the regularised incomplete beta identity:
      P(|T| >= |t|) = I_{df/(df+t^2)}(df/2, 1/2)
    Computed via mpmath.betainc(..., regularized=True).
    """
    import mpmath
    mpmath.mp.dps = 30
    t_abs = abs(float(t_stat))
    if df <= 0:
        return float('nan')
    x = mpmath.mpf(df) / (mpmath.mpf(df) + mpmath.mpf(t_abs)**2)
    p = mpmath.betainc(mpmath.mpf(df) / 2, mpmath.mpf('0.5'), 0, x, regularized=True)
    return float(p)


def binomial_two_tail_p(k, n, p=0.5):
    """Exact two-tailed binomial test p-value, null = p.

    Sums probabilities of outcomes at least as extreme (in either direction)
    as the observed k. For p=0.5 this reduces to twice the more-extreme tail.
    Uses mpmath for numerical safety at large n.
    """
    import mpmath
    mpmath.mp.dps = 40
    n_mp = int(n)
    k = int(k)
    p_mp = mpmath.mpf(p)
    q_mp = 1 - p_mp

    def pmf(j):
        return mpmath.binomial(n_mp, j) * p_mp**j * q_mp**(n_mp - j)

    p_obs = pmf(k)
    total = mpmath.mpf(0)
    for j in range(0, n_mp + 1):
        pj = pmf(j)
        if pj <= p_obs * (1 + mpmath.mpf('1e-30')):
            total += pj
    return float(min(total, mpmath.mpf(1)))


if __name__ == '__main__':
    # Sanity: spot-check chi5 values against the brief's hand list.
    # primes ≡ 1 mod 4: 5, 13, 17, 29, 37, 41, 53, 61, 73, 89
    expected = {5: 0, 13: -1, 17: -1, 29: 1, 37: -1, 41: 1,
                53: -1, 61: 1, 73: -1, 89: 1}
    for p, want in expected.items():
        got = chi5(p)
        ok = 'OK' if got == want else 'FAIL'
        print(f"  chi5({p}) = {got} (want {want}) {ok}")
