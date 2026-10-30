"""The prime arrays to 1e9 that both figures draw their measured curve from.

About 800 MB written to work/ (not committed), about 3 GB of memory, 33 s on
the 7 October Linux machine. The 5-series is the primes of the form 6k+5, the
7-series those of the form 6k+1; L5 and L7 are the cumulative sums of log10 p.
"""

import time

import numpy as np
from common import WORK, Log, describe_longdouble

LIMIT = 1_000_000_000


def main():
    with Log("step4_big") as log:
        start_time = time.time()
        log(describe_longdouble())
        sieve = np.ones(LIMIT + 1, dtype=bool)
        sieve[:2] = False
        sieve[4::2] = False
        for i in range(3, int(LIMIT**0.5) + 1, 2):
            if sieve[i]:
                sieve[i * i :: 2 * i] = False
        primes = np.flatnonzero(sieve)
        del sieve
        log(f"primes <= 1e9: {len(primes)}  {time.time() - start_time:.1f}s")
        residues = primes % 6
        series_5 = primes[residues == 5]
        series_7 = primes[residues == 1]
        del primes, residues
        log(f"5-series {len(series_5)}, 7-series {len(series_7)}")
        log5 = np.cumsum(
            np.log10(series_5.astype(np.float64)).astype(np.longdouble)
        ).astype(np.float64)
        log7 = np.cumsum(
            np.log10(series_7.astype(np.float64)).astype(np.longdouble)
        ).astype(np.float64)
        log(
            f"digits reached: {log5[-1]:.0f} and {log7[-1]:.0f}"
            f"   {time.time() - start_time:.1f}s"
        )
        WORK.mkdir(exist_ok=True)
        np.save(WORK / "big_s5.npy", series_5)
        np.save(WORK / "big_s7.npy", series_7)
        np.save(WORK / "big_L5.npy", log5)
        np.save(WORK / "big_L7.npy", log7)
        log(f"elapsed {time.time() - start_time:.1f}s")


if __name__ == "__main__":
    main()
