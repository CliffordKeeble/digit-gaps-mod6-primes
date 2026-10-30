"""The lead from 1e11 to 1e12, measured and rebuilt: writes work/p11_curve.npy.

The sieve of 1e11 to 1e12 (data/p11_segments.npy: one row per segment of 5e7)
gives the measured rise of the lead, J. recon.py and the zeros give the rebuilt
one. The starting counts and sums at 1e11 are read from the 1e+11 row of
data/step12_sieve_1e11.log, not typed. The two curves are stacked as rows
[x, measured rise, rebuilt rise] for fig_zeros.py.
"""

import math
import re
import time

import numpy as np
import recon
from common import DATA, WORK, Log

SEGMENT = 5 * 10**7
# pi(1e12) - pi(1e11), a published count of primes (the independent check on the sieve)
PRIMES_BETWEEN = 37607912018 - 4118054813


def starting_values_at_1e11():
    """pi5, pi7 and theta5 - theta7 at 1e11, from the sieve log's 1e+11 row."""
    pattern = re.compile(r"^\s*1e\+11\s+(\d+)\s+(\d+)\s+(-?\d+)\s+(-?[\d.]+)\s")
    for line in (DATA / "step12_sieve_1e11.log").read_text().splitlines():
        match = pattern.match(line)
        if match:
            count_5, count_7, difference = (int(match.group(i)) for i in (1, 2, 3))
            assert count_5 - count_7 == difference, "the log row disagrees with itself"
            return count_5, count_7, float(match.group(4))
    raise SystemExit("data/step12_sieve_1e11.log has no 1e+11 row")


def main():
    with Log("step18_curve") as log:
        start_time = time.time()
        segments = np.load(DATA / "p11_segments.npy")
        segments = segments[np.argsort(segments[:, 0])]
        index = segments[:, 0].astype(np.int64)
        counts_5 = segments[:, 1].astype(np.int64)
        counts_7 = segments[:, 2].astype(np.int64)
        sums_5 = segments[:, 3]
        sums_7 = segments[:, 4]
        assert len(index) == 18000 and index[0] == 2000 and index[-1] == 19999
        assert (np.diff(index) == 1).all()
        total = int(counts_5.sum() + counts_7.sum())
        log(
            f"primes counted in (1e11, 1e12): {total} ; pi(1e12) - pi(1e11) = "
            f"{PRIMES_BETWEEN} ; {'AGREE' if total == PRIMES_BETWEEN else 'DISAGREE'}"
        )
        start_5, start_7, start_theta = starting_values_at_1e11()
        log(
            f"starting values at 1e11, read from the sieve log: pi5 = {start_5}, "
            f"pi7 = {start_7}, theta5 - theta7 = {start_theta}"
        )
        cumulative_5 = start_5 + np.cumsum(counts_5)
        cumulative_7 = start_7 + np.cumsum(counts_7)
        theta_difference = start_theta + np.cumsum(sums_5 - sums_7)
        x = (index + 1).astype(np.float64) * SEGMENT
        lead = (cumulative_5 - cumulative_7) - theta_difference / np.log(x)
        lead_at_start = (start_5 - start_7) - start_theta / math.log(1e11)
        rise = lead - lead_at_start

        zeros = np.load(DATA / "zeros_chi3_T3000.npy")
        bias = recon.Bias(10**12)

        def rebuilt(points):
            return (
                bias.H(points) + recon.Zs(points, zeros) - recon.BCHI / np.log(points)
            )

        base = rebuilt(np.array([1e11]))[0]
        full = rebuilt(x) - base
        residual = full - rise
        log(
            f"every segment end (18,000 points, steps of 5e7): largest |measured - "
            f"rebuilt| {np.abs(residual).max():.4f}, rms {math.sqrt((residual**2).mean()):.4f}"
        )
        log(f"the lead at 1e12: {lead[-1]:.2f}")
        WORK.mkdir(exist_ok=True)
        np.save(WORK / "p11_curve.npy", np.vstack([x, rise, full]))
        log(f"elapsed {time.time() - start_time:.0f} s")


if __name__ == "__main__":
    main()
