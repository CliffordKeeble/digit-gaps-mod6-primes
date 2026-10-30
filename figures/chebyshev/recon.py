"""The lead rebuilt from first principles: BIAS + ZEROS + CONSTANT.  Nothing fitted.

chi = the non-principal character mod 3 (chi(p) = +1 for the 7-series, -1 for the 5-series and for 2).
  theta5(t) - theta7(t) = F(t) - psi(t, chi)                                  (exact)
  F(t)  = sum over prime powers p^k <= t, k >= 2, p >= 5, of chi(p)^k ln p
          + ln 2 * sum over 2^k <= t, k >= 1, of (-1)^k
  J(x)  = [pi5 - pi7](x) - [theta5 - theta7](x)/ln x ,   J(b) - J(a) = integral_a^b (theta5 - theta7)/(t ln^2 t) dt
  psi(t, chi) = - sum_rho t^rho/rho - b(chi) + (artanh(1/t), dropped),  b(chi) = L'(0,chi)/L(0,chi) = 0.948198826673
so  J(b) - J(a) = [Hb + Zs - b(chi)/ln x] from a to b, with
  Hb(x) = sum_{q <= x} w_q (1/ln q - 1/ln x)            (q the prime powers above, w_q their weights)
  Zs(x) = sum over zeros gamma > 0 of 2 Re[ x^rho * sum_{k>=1} k!/(rho ln x)^(k+1) ],  rho = 1/2 + i gamma.
(Ported from the 7 October 2026 review's recon.py, unchanged in what it computes.)
"""

import math

import numpy as np

LN10 = math.log(10.0)
BCHI = 3 * (math.lgamma(1 / 3) - math.lgamma(2 / 3)) - math.log(3)


def primes_upto(n):
    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = False
    return np.flatnonzero(sieve)


def jump_list(xmax=10**12, squares_only=False):
    prime_powers = []
    weights = []
    for p in primes_upto(math.isqrt(xmax) + 1).tolist():
        if p == 3:
            continue
        if p == 2:
            if squares_only:
                continue
            q, k = 2, 1
            while q <= xmax:
                prime_powers.append(q)
                weights.append(math.log(2) * (-1) ** k)
                q *= 2
                k += 1
            continue
        chi = 1 if p % 3 == 1 else -1
        q, k = p * p, 2
        while q <= xmax:
            prime_powers.append(q)
            weights.append(math.log(p) * chi**k)
            if squares_only:
                break
            q *= p
            k += 1
    prime_powers = np.array(prime_powers, dtype=float)
    weights = np.array(weights)
    order = np.argsort(prime_powers)
    return prime_powers[order], weights[order]


class Bias:
    def __init__(self, xmax=10**12, squares_only=False):
        self.q, self.w = jump_list(xmax, squares_only)
        self.c0 = np.cumsum(self.w)
        self.c1 = np.cumsum(self.w / np.log(self.q))

    def F(self, x):
        x = np.atleast_1d(np.asarray(x, float))
        i = np.searchsorted(self.q, x, side="right") - 1
        return np.where(i >= 0, self.c0[np.clip(i, 0, None)], 0.0)

    def H(self, x):
        x = np.atleast_1d(np.asarray(x, float))
        i = np.searchsorted(self.q, x, side="right") - 1
        j = np.clip(i, 0, None)
        return np.where(i >= 0, self.c1[j] - self.c0[j] / np.log(x), 0.0)


def Zs(x, gammas, K=14, chunk=800):
    x = np.atleast_1d(np.asarray(x, float))
    out = np.empty(len(x))
    rho = 0.5 + 1j * np.asarray(gammas, float)
    for i in range(0, len(x), chunk):
        z = np.outer(np.log(x[i : i + chunk]), rho)
        inv = 1.0 / z
        term = inv * inv
        series = term.copy()
        for k in range(2, K + 1):
            term = term * (k * inv)
            series += term  # k!/z^(k+1)
        out[i : i + chunk] = 2 * np.real(np.exp(z) * series).sum(axis=1)
    return out
