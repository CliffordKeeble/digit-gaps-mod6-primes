"""Figure 2: the lead's wobble about the smooth bias curve, measured, against
the sum over the zeros of L(s, chi mod 3). Nothing fitted: the rebuilt curve
starts from the measured lead at primes of 1e4 and takes the zeros as filed.

The lead is counted at each prime size here (J(x) = pi5 - pi7 - (theta5 - theta7)/ln x).
Every number printed on the figure is computed here and printed to
logs/fig_zeros.log. Refuses to draw without the decade 1e11 to 1e12
(work/p11_curve.npy, made by step18_curve.py), and from a dirty tree.
"""

import math
import re
import sys

import matplotlib
import numpy as np
import recon
from common import (
    DATA,
    IMAGES,
    WORK,
    Log,
    describe_longdouble,
    require_file,
    source_state,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BACKGROUND = "#14161a"
FOREGROUND = "#e8e6e1"
GRID = "#3a3f48"
CURVE = "#6fb7ff"
DOT = "#ffb454"
THEORY = "#ff6b81"

START_PRIME_SIZE = 1e4
LN10 = recon.LN10


def main():
    with Log("fig_zeros") as log:
        commit, date = source_state()
        log(f"scripts and data at commit {commit}, {date}")
        log(describe_longdouble())
        require_file(
            WORK / "p11_curve.npy",
            "the decade 1e11 to 1e12 cannot be drawn without it; run step18_curve.py "
            "(refusing to draw a figure with that decade missing)",
        )
        for name in ("big_s5.npy", "big_s7.npy", "big_L5.npy", "big_L7.npy"):
            require_file(WORK / name, "run step4_big.py")

        zeros = np.load(DATA / "zeros_chi3_T3000.npy")
        assert zeros.max() < 3000
        zero_count = len(zeros)
        log(f"zeros of L(s, chi_-3) in the file: {zero_count}, all below height 3000")
        bias = recon.Bias(10**12)
        # in memory: searchsorted on a memmap re-reads the file at every call
        prime_5 = np.load(WORK / "big_s5.npy")
        prime_7 = np.load(WORK / "big_s7.npy")
        log_5 = np.load(WORK / "big_L5.npy")
        log_7 = np.load(WORK / "big_L7.npy")

        def lead_exact(x):
            x = np.atleast_1d(np.asarray(x, float))
            index_5 = np.searchsorted(prime_5, x, side="right")
            index_7 = np.searchsorted(prime_7, x, side="right")
            return (index_5 - index_7) - (
                log_5[index_5 - 1] - log_7[index_7 - 1]
            ) * LN10 / np.log(x)

        def smooth(x):
            # bias + constant: everything but the zeros
            return bias.H(x) - recon.BCHI / np.log(x)

        def lead_size(x):
            return 2 * np.sqrt(x) / np.log(x) ** 2

        # measured: dense to 1e9, the sieve's checkpoints to 1e11, every segment end to 1e12
        dense_x = np.exp(
            np.linspace(math.log(START_PRIME_SIZE), math.log(9.999e8), 5000)
        )
        dense_lead = lead_exact(dense_x)
        lead_start = lead_exact(START_PRIME_SIZE)[0]
        checkpoint_lead = {}
        for line in (DATA / "step12_sieve_1e11.log").read_text().splitlines():
            match = re.match(
                r"\s*(\de\+\d\d)\s+(\d+)\s+(\d+)\s+(-?\d+)\s+(-?[\d.]+)\s", line
            )
            if match:
                x = float(match.group(1))
                checkpoint_lead[x] = int(match.group(4)) - float(
                    match.group(5)
                ) / math.log(x)
        checkpoint_x = np.array(sorted(checkpoint_lead))
        checkpoint_values = np.array([checkpoint_lead[x] for x in checkpoint_x]) + (
            lead_exact(1e9)[0] - checkpoint_lead[1e9]
        )
        curve = np.load(WORK / "p11_curve.npy")
        decade_x = curve[0]
        decade_lead = checkpoint_values[-1] + curve[1]
        decade_residual = (
            curve[1] - curve[2]
        )  # measured minus rebuilt, from step18_curve.py
        smooth_start = smooth(np.array([START_PRIME_SIZE]))[0]

        def wobble(x, lead):
            # measured wobble: rise minus the smooth part
            return (lead - lead_start) - (smooth(x) - smooth_start)

        grid_x = np.exp(np.linspace(math.log(START_PRIME_SIZE), math.log(1e12), 9000))
        zero_start = recon.Zs(np.array([START_PRIME_SIZE]), zeros)[0]
        zero_sum = recon.Zs(grid_x, zeros) - zero_start
        first_zero_sum = (
            recon.Zs(grid_x, zeros[:1])
            - recon.Zs(np.array([START_PRIME_SIZE]), zeros[:1])[0]
        )

        def residual(x, lead):
            return wobble(x, lead) - (recon.Zs(x, zeros) - zero_start)

        resid_dense = residual(dense_x, dense_lead)
        resid_checkpoints = residual(checkpoint_x, checkpoint_values)
        largest = max(
            np.abs(resid_dense).max(),
            np.abs(resid_checkpoints).max(),
            np.abs(decade_residual).max(),
        )
        bound = math.ceil(largest * 100) / 100
        lead_at_1e12 = decade_lead[-1]
        log(
            f"largest |measured - rebuilt|: to 1e9 {np.abs(resid_dense).max():.4f}, "
            f"checkpoints {np.abs(resid_checkpoints).max():.4f}, "
            f"decade 1e11 to 1e12 {np.abs(decade_residual).max():.4f}"
        )
        log(
            f"largest of the three {largest:.4f}, printed on the figure as within {bound:.2f}"
        )
        log(f"the lead at 1e12: {lead_at_1e12:.2f}, printed as {lead_at_1e12:,.0f}")
        log(f"checkpoints drawn: {len(checkpoint_x)}")
        # the red line as drawn (linear in log x between its grid points), read at the
        # checkpoint sizes, against the rebuilt value there, in the upper panel's units
        drawn_at_checkpoints = np.interp(
            np.log(checkpoint_x), np.log(grid_x), 100 * zero_sum / lead_size(grid_x)
        )
        rebuilt_at_checkpoints = (
            100 * (recon.Zs(checkpoint_x, zeros) - zero_start) / lead_size(checkpoint_x)
        )
        line_gap = np.abs(drawn_at_checkpoints - rebuilt_at_checkpoints).max()
        marker_gap = np.abs(
            100 * wobble(checkpoint_x, checkpoint_values) / lead_size(checkpoint_x)
            - drawn_at_checkpoints
        ).max()
        log(
            f"largest gap between the red line as drawn and the rebuilt value, over the "
            f"{len(checkpoint_x)} checkpoint sizes: {line_gap:.4f} (percentage points)"
        )
        log(
            f"largest gap between a checkpoint marker and the red line as drawn: "
            f"{marker_gap:.4f} (percentage points)"
        )
        if line_gap >= 0.05:
            sys.exit(
                "the red line misses the rebuilt values at the checkpoints by 0.05 or more"
            )
        log(f"prime size to digits: x / {2 * LN10:.1f}")

        plt.rcParams.update(
            {
                "font.size": 13,
                "font.family": "DejaVu Sans",
                "axes.edgecolor": GRID,
                "axes.labelcolor": FOREGROUND,
                "xtick.color": FOREGROUND,
                "ytick.color": FOREGROUND,
                "text.color": FOREGROUND,
                "figure.facecolor": BACKGROUND,
                "axes.facecolor": BACKGROUND,
                "savefig.facecolor": BACKGROUND,
            }
        )
        figure, (top, bottom) = plt.subplots(
            2,
            1,
            figsize=(15, 9.2),
            gridspec_kw={"height_ratios": [2.6, 1], "hspace": 0.13},
            sharex=True,
        )
        top.axhline(0, color=GRID, lw=1)
        top.plot(
            grid_x,
            100 * first_zero_sum / lead_size(grid_x),
            color=FOREGROUND,
            lw=1.0,
            alpha=0.35,
            label="the first zero alone (height 8.04)",
            zorder=2,
        )
        top.plot(
            dense_x,
            100 * wobble(dense_x, dense_lead) / lead_size(dense_x),
            color=CURVE,
            lw=4.2,
            alpha=0.55,
            label="measured, primes to 10⁹",
            zorder=3,
        )
        top.plot(
            checkpoint_x,
            100 * wobble(checkpoint_x, checkpoint_values) / lead_size(checkpoint_x),
            lw=0,
            marker="o",
            ms=7,
            mfc=BACKGROUND,
            mec=CURVE,
            mew=1.8,
            label=f"measured, 10⁹ to 10¹¹ ({len(checkpoint_x)} checkpoints)",
            zorder=6,
        )
        top.plot(
            decade_x,
            100 * wobble(decade_x, decade_lead) / lead_size(decade_x),
            color=DOT,
            lw=4.2,
            alpha=0.6,
            label="measured, 10¹¹ to 10¹² (sieve segments)",
            zorder=3,
        )
        top.plot(
            grid_x,
            100 * zero_sum / lead_size(grid_x),
            color=THEORY,
            lw=1.3,
            label=f"rebuilt from the {zero_count:,} zeros of L(s, χ₋₃) below height 3000",
            zorder=5,
        )
        top.set_xscale("log")
        top.set_xlim(1e4, 1e12)
        top.set_ylabel(
            "wobble of the lead, counted at each prime size,\nas % of its size  2√x / ln²x"
        )
        top.set_title(
            "The lead's wobble about the smooth bias curve is the zeros of one L-function. "
            "Nothing is fitted.",
            fontsize=15,
            pad=12,
            loc="left",
        )
        top.set_ylim(-6.3, 4.1)
        top.set_yticks(range(-3, 4))
        top.grid(True, which="major", color=GRID, lw=0.6)
        top.legend(
            loc="lower left",
            frameon=True,
            facecolor=BACKGROUND,
            edgecolor=GRID,
            fontsize=11,
            ncol=2,
            columnspacing=1.6,
            title="the lead, counted at each prime size",
            title_fontsize=11,
        )
        top.axvspan(1e11, 1e12, color=DOT, alpha=0.06, lw=0)

        # residual panel: measured minus rebuilt, in primes
        bottom.axhline(0, color=GRID, lw=1)
        bottom.plot(dense_x, resid_dense, color=CURVE, lw=1.2)
        bottom.plot(
            checkpoint_x,
            resid_checkpoints,
            lw=0,
            marker="o",
            ms=5.5,
            mfc=BACKGROUND,
            mec=CURVE,
            mew=1.5,
        )
        bottom.plot(decade_x, decade_residual, color=DOT, lw=1.0)
        bottom.axvspan(1e11, 1e12, color=DOT, alpha=0.06, lw=0)
        bottom.set_ylim(-0.04, 0.04)
        bottom.set_ylabel("measured − rebuilt\n(primes)")
        bottom.set_xlabel(
            f"prime size x   (the 5-series' product has about x / {2 * LN10:.1f} digits)"
        )
        bottom.grid(True, which="major", color=GRID, lw=0.6)
        bottom.text(
            1.2e4,
            0.036,
            f"the lead climbs to {lead_at_1e12:,.0f} primes at 10¹²; "
            f"measured minus rebuilt stays within {bound:.2f} of a prime",
            fontsize=10.5,
            va="top",
            alpha=0.9,
        )
        figure.text(
            0.01,
            0.005,
            "5-series: primes of the form 6k+5. The rebuilt curve takes one starting value, "
            "the measured lead at primes of 10⁴, and fits nothing. "
            f"Scripts and data: commit {commit}, regenerated {date}.",
            fontsize=10,
            alpha=0.7,
        )
        IMAGES.mkdir(parents=True, exist_ok=True)
        figure.savefig(IMAGES / "chebyshev_zeros.png", dpi=110, bbox_inches="tight")
        log("saved docs/img/chebyshev_zeros.png")


if __name__ == "__main__":
    main()
