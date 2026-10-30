"""Chebyshev's bias through the digit-lengths of two prime products.

Standard library only. This one file is what the demo page runs in the browser
(under Pyodide) and what pytest tests, so the page never runs a copy.

The two products are over the primes p <= bound with p % 6 == 5 and with
p % 6 == 1. The first is slightly the larger, because primes of the form 6k+5
are slightly more common than primes of the form 6k+1 (Chebyshev, 1853).
"""

import itertools
import math
import time
from collections.abc import Sequence

LOG10_2 = math.log10(2)

ALLOWED_BOUNDS = (10**5, 10**6, 2 * 10**6, 5 * 10**6, 10**7)

# The keys race() returns, in order. docs/app.js carries the same list and a
# test compares the two, so a key renamed in one place goes red.
RESULT_KEYS = (
    "bound",
    "count_5_mod_6",
    "count_1_mod_6",
    "digits_5_mod_6",
    "digits_1_mod_6",
    "digit_difference",
    "larger",
    "seconds_sieve",
    "seconds_multiply",
    "seconds_digit_count",
    "seconds_total",
)

# The keys float_trap() returns, in order; docs/app.js carries the same list.
TRAP_KEYS = (
    "float_route",
    "exact",
    "difference",
    "leading_digits_agree",
    "float_digits",
    "exact_digits",
    "float_mod_3",
    "exact_mod_3",
)


def primes_upto(n: int) -> list[int]:
    """All primes <= n, by a sieve of Eratosthenes over a bytearray."""
    if n < 2:
        return []
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0] = is_prime[1] = 0
    is_prime[4::2] = bytes(len(range(4, n + 1, 2)))
    for candidate in range(3, math.isqrt(n) + 1, 2):
        if is_prime[candidate]:
            start = candidate * candidate
            is_prime[start :: 2 * candidate] = bytes(
                len(range(start, n + 1, 2 * candidate))
            )
    return list(itertools.compress(range(n + 1), is_prime))


def product_tree(factors: Sequence[int]) -> int:
    """The product of the factors, multiplied pairwise level by level.

    A running product multiplies a huge number by a small one n times, which
    is quadratic; the tree multiplies numbers of equal size. No factors give 1.
    """
    level = list(factors)
    if not level:
        return 1
    while len(level) > 1:
        next_level = [
            level[index] * level[index + 1] for index in range(0, len(level) - 1, 2)
        ]
        if len(level) % 2:
            next_level.append(level[-1])
        level = next_level
    return level[0]


def _correct_digit_estimate(n: int, estimate: int) -> int:
    """Move a digit-count estimate of n > 0 to the true count.

    Down while n < 10**(estimate - 1), up while n >= 10**estimate.
    """
    estimate = max(estimate, 1)
    power_of_ten = 10 ** (estimate - 1)  # the smallest number of `estimate` digits
    while n < power_of_ten:
        estimate -= 1
        power_of_ten //= 10
    while n >= power_of_ten * 10:
        estimate += 1
        power_of_ten *= 10
    return estimate


def digit_count(n: int) -> int:
    """The number of decimal digits of n > 0, without str().

    Since Python 3.11, str() of an int over 4,300 digits raises by default, and
    the products here run to millions of digits. The bit length gives an
    estimate that is out by at most one; the correction makes it exact.
    """
    if n <= 0:
        raise ValueError("digit_count needs n > 0")
    estimate = int(n.bit_length() * LOG10_2) + 1
    return _correct_digit_estimate(n, estimate)


def race(bound: int) -> dict:
    """Count, multiply and measure the two prime products up to `bound`.

    Refuses any bound not in ALLOWED_BOUNDS: a visitor's browser must not be
    handed a size that never finishes.
    """
    if type(bound) is not int or bound not in ALLOWED_BOUNDS:
        raise ValueError(f"bound must be one of {ALLOWED_BOUNDS}, got {bound!r}")
    start_total = time.perf_counter()

    start = time.perf_counter()
    primes = primes_upto(bound)
    seconds_sieve = time.perf_counter() - start

    start = time.perf_counter()
    primes_5_mod_6 = [prime for prime in primes if prime % 6 == 5]
    primes_1_mod_6 = [prime for prime in primes if prime % 6 == 1]
    product_5_mod_6 = product_tree(primes_5_mod_6)
    product_1_mod_6 = product_tree(primes_1_mod_6)
    seconds_multiply = time.perf_counter() - start

    start = time.perf_counter()
    digits_5_mod_6 = digit_count(product_5_mod_6)
    digits_1_mod_6 = digit_count(product_1_mod_6)
    seconds_digit_count = time.perf_counter() - start

    if product_5_mod_6 > product_1_mod_6:
        larger = "5 mod 6"
    elif product_5_mod_6 < product_1_mod_6:
        larger = "1 mod 6"
    else:
        larger = "equal"

    return {
        "bound": bound,
        "count_5_mod_6": len(primes_5_mod_6),
        "count_1_mod_6": len(primes_1_mod_6),
        "digits_5_mod_6": digits_5_mod_6,
        "digits_1_mod_6": digits_1_mod_6,
        "digit_difference": digits_5_mod_6 - digits_1_mod_6,
        "larger": larger,
        "seconds_sieve": seconds_sieve,
        "seconds_multiply": seconds_multiply,
        "seconds_digit_count": seconds_digit_count,
        "seconds_total": time.perf_counter() - start_total,
    }


def float_trap(n: int = 61) -> dict:
    """10**n by the float route against the exact integer.

    The float route is floor(exp(n * ln 10)). A double holds about 16
    significant digits, so for n = 61 it gets the length right and the digits
    after the first dozen or so wrong. Everything comes back as decimal
    strings (62 digits is under the str() limit): a JavaScript Number would
    round a 62-digit integer, which is the very error shown, and JSON.stringify
    refuses a BigInt.
    """
    if n < 0:
        raise ValueError("float_trap needs n >= 0")
    float_route = math.floor(math.exp(n * math.log(10)))
    exact = 10**n
    float_text = str(float_route)
    exact_text = str(exact)
    leading_digits_agree = sum(
        1
        for _ in itertools.takewhile(
            lambda pair: pair[0] == pair[1], zip(float_text, exact_text)
        )
    )
    return {
        "float_route": float_text,
        "exact": exact_text,
        "difference": str(exact - float_route),
        "leading_digits_agree": leading_digits_agree,
        "float_digits": digit_count(float_route),
        "exact_digits": digit_count(exact),
        "float_mod_3": float_route % 3,
        "exact_mod_3": exact % 3,
    }
