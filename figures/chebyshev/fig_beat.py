"""Figure 1: digit gaps in the two prime products, a beat between two staircases.

Left, the lead at the 13 synchronisation clusters. Right, the lead against the
classical curve (one starting value, nothing fitted) and a fixed-exponent power
law (one fitted constant, A). Every number printed on the figure is computed
here and printed to logs/fig_beat.log. Refuses to draw from a dirty tree.
"""

import math
import re

import matplotlib
import numpy as np
from common import (
    DATA,
    IMAGES,
    WORK,
    Log,
    describe_longdouble,
    lead_at_index,
    require_file,
    source_state,
)
from scipy.integrate import quad

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BACKGROUND = "#14161a"
FOREGROUND = "#e8e6e1"
GRID = "#3a3f48"
CURVE = "#6fb7ff"
DOT = "#ffb454"
THEORY = "#ff6b81"
POWER = "#7bd88f"

EXPONENT = 1 - math.log(2) / math.log(3)
FIT_EDGES = [1e4, 1e5, 1e6, 1e7, 1e8, 9.8e8]  # the rise from primes of 1e4 to 9.8e8
START_PRIME_SIZE = 1e4  # the classical curve's one starting value


def classical_integrand(t):
    return 1.0 / (math.sqrt(t) * math.log(t) ** 2)


def read_checkpoints():
    """(x, lead, digits) of the sieve to 1e11, from its log: 19 rows, 1e9 to 1e11."""
    pattern = re.compile(
        r"\s*(\d)e\+(\d+)\s+\d+\s+\d+\s+\d+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+(\d+)\s*$"
    )
    rows = []
    for line in (DATA / "step12_sieve_1e11.log").read_text().splitlines():
        match = pattern.match(line)
        if match:
            x = int(match.group(1)) * 10 ** int(match.group(2))
            rows.append((x, float(match.group(3)), float(match.group(4))))
    checkpoints = np.array(sorted(set(rows)))
    assert len(checkpoints) == 19
    assert checkpoints[0, 0] == 1e9 and checkpoints[-1, 0] == 1e11
    return checkpoints


def reference_value(log_name, pattern):
    text = (DATA / log_name).read_text()
    return float(re.search(pattern, text).group(1))


def fit_constant(prime_5, log_5, log_7, log):
    """C1: the constant of the fixed-exponent power law, fitted, not typed.

    lead rise = A * (D^e - D0^e) over the primes of 1e4 to 9.8e8, e = 1 - ln2/ln3
    (step 11 of the 7 October review, whose log prints A = 0.15895).
    """
    indices = [
        int(np.searchsorted(prime_5, edge, side="right")) - 1 for edge in FIT_EDGES
    ]
    leads = [float(lead_at_index(log_5, log_7, index)) for index in indices]
    digits = [float(log_5[index]) + 1 for index in indices]
    constant = (leads[-1] - leads[0]) / (digits[-1] ** EXPONENT - digits[0] ** EXPONENT)
    reference = reference_value(
        "reference_step11_powerlaw_vs_classical.log", r"fitted constant A = ([\d.]+)"
    )
    log(
        f"A (fixed-exponent constant), fitted here: {constant:.5f} ; "
        f"step 11 log of 7 October: {reference:.5f} ; "
        f"{'AGREE to 5 decimal places' if f'{constant:.5f}' == f'{reference:.5f}' else 'DIFFER'}"
    )
    return constant


def cluster_levels(centres, digits, lead, log):
    """C2: the lead at the 13 centres found by step1_clusters.py, and how near
    a whole number each is."""
    at_centres = np.interp(centres, digits, lead)
    nearest = np.rint(at_centres).astype(int)
    deviation = np.abs(at_centres - nearest)
    log(f"the {len(centres)} cluster centres: {centres.tolist()}")
    log(f"lead at the centres: {np.round(at_centres, 4).tolist()}")
    log(f"nearest whole numbers: {nearest.tolist()}")
    log(f"largest distance from a whole number: {deviation.max():.4f}")
    if nearest.tolist() != list(range(2, 2 + len(centres))):
        raise SystemExit("the centres are not at 2, 3, 4, ...: not drawing")
    return nearest, math.ceil(deviation.max() * 1000) / 1000


def main():
    with Log("fig_beat") as log:
        commit, date = source_state()
        log(f"scripts and data at commit {commit}, {date}")
        log(describe_longdouble())
        for name, how in (
            ("big_s5.npy", "run step4_big.py"),
            ("big_s7.npy", "run step4_big.py"),
            ("big_L5.npy", "run step4_big.py"),
            ("big_L7.npy", "run step4_big.py"),
            ("cluster_centres.npy", "run step1_clusters.py"),
        ):
            require_file(WORK / name, how)
        prime_5 = np.load(WORK / "big_s5.npy", mmap_mode="r")
        log_5 = np.load(WORK / "big_L5.npy", mmap_mode="r")
        log_7 = np.load(WORK / "big_L7.npy", mmap_mode="r")
        centres = np.load(WORK / "cluster_centres.npy")
        checkpoints = read_checkpoints()
        constant = fit_constant(prime_5, log_5, log_7, log)

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
        figure, (panel_a, panel_b) = plt.subplots(
            1, 2, figsize=(17, 7.8), gridspec_kw={"width_ratios": [1.08, 1]}
        )

        # ---------- panel A: the mechanism
        count = int(np.searchsorted(log_5, 205_000))
        indices = np.arange(20, count)
        digits = np.asarray(log_5[indices]) + 1
        lead = lead_at_index(log_5, log_7, indices)
        for level in range(1, 15):
            panel_a.axhline(level, color=GRID, lw=0.8, zorder=1)
        panel_a.plot(
            digits,
            lead,
            color=CURVE,
            lw=1.6,
            zorder=3,
            label="lead = extra primes the 5-series needs to reach the same size",
        )
        nearest, bound = cluster_levels(centres, digits, lead, log)
        panel_a.scatter(
            centres,
            np.interp(centres, digits, lead),
            s=95,
            color=DOT,
            edgecolor=BACKGROUND,
            lw=1.2,
            zorder=5,
            label="the 13 synchronisation clusters reported in the paper (v2.3)",
        )
        panel_a.set_xscale("log")
        panel_a.set_xlim(100, 215_000)
        panel_a.set_ylim(0.6, 15)
        panel_a.set_yticks(range(1, 15))
        panel_a.set_xlabel("digit-length of the product")
        panel_a.set_ylabel("lead (primes)")
        panel_a.set_title(
            "Every cluster sits where the lead is a whole number",
            fontsize=15,
            pad=12,
            loc="left",
        )
        panel_a.legend(
            loc="upper left",
            frameon=True,
            facecolor=BACKGROUND,
            edgecolor=GRID,
            fontsize=11.5,
        )
        levels = f"{nearest[0]}, {nearest[1]}, {nearest[2]}, … {nearest[-1]}"
        panel_a.text(
            0.985,
            0.04,
            f"lead at the {len(centres)} cluster centres: within {bound:.3f} of {levels}",
            transform=panel_a.transAxes,
            ha="right",
            va="bottom",
            fontsize=11,
            alpha=0.85,
        )

        # ---------- panel B: the cause, and the two decades beyond the dense data
        last_index = int(np.searchsorted(log_5, min(log_5[-1], log_7[-1]) - 10))
        grid_indices = np.unique(
            np.round(
                np.exp(np.linspace(math.log(30), math.log(last_index - 1), 3000))
            ).astype(np.int64)
        )
        digits_grid = np.asarray(log_5[grid_indices]) + 1
        lead_grid = lead_at_index(log_5, log_7, grid_indices)
        prime_grid = np.asarray(prime_5[grid_indices]).astype(float)
        start_index = int(np.searchsorted(prime_5, START_PRIME_SIZE))
        lead_start = float(lead_at_index(log_5, log_7, np.array([start_index]))[0])
        digits_start = float(log_5[start_index]) + 1
        log(
            f"the classical curve's one starting value: lead {lead_start:.3f} "
            f"at primes of 1e4 (digit-length {digits_start:.0f})"
        )
        sizes = np.exp(np.linspace(math.log(START_PRIME_SIZE), math.log(1e11), 500))
        cumulative = np.concatenate(
            [
                [0.0],
                np.cumsum(
                    [
                        quad(classical_integrand, sizes[j], sizes[j + 1])[0]
                        for j in range(len(sizes) - 1)
                    ]
                ),
            ]
        )
        all_sizes = np.concatenate([prime_grid, checkpoints[1:, 0]])
        all_digits = np.concatenate([digits_grid, checkpoints[1:, 2]])
        digits_at_sizes = np.interp(np.log(sizes), np.log(all_sizes), all_digits)

        panel_b.plot(
            digits_grid,
            lead_grid,
            color=CURVE,
            lw=2.2,
            label="measured, primes to 10⁹",
            zorder=3,
        )
        panel_b.plot(
            checkpoints[:, 2],
            checkpoints[:, 1],
            color=CURVE,
            lw=0,
            marker="o",
            ms=5.5,
            mfc=BACKGROUND,
            mec=CURVE,
            mew=1.5,
            label="measured, sieve checkpoints 10⁹ to 10¹¹",
            zorder=6,
        )
        panel_b.plot(
            digits_at_sizes,
            lead_start + cumulative,
            color=THEORY,
            lw=1.8,
            ls=(0, (5, 3)),
            label=(
                "classical curve ∫ dt / (√t · ln²t):\n"
                "one starting value, the measured lead at primes of 10⁴; fits nothing"
            ),
            zorder=4,
        )
        panel_b.plot(
            digits_at_sizes,
            lead_start
            + constant * (digits_at_sizes**EXPONENT - digits_start**EXPONENT),
            color=POWER,
            lw=1.6,
            ls=(0, (1, 2)),
            label="fixed exponent ln2/ln3: one fitted number",
            zorder=4,
        )
        panel_b.set_xscale("log")
        panel_b.set_yscale("log")
        panel_b.set_xlim(300, 4e10)
        panel_b.set_ylim(1.2, 2600)
        panel_b.set_xlabel("digit-length of the product")
        panel_b.set_ylabel("lead (primes)")
        panel_b.set_title(
            "…and the lead follows Chebyshev's bias, a classical result",
            fontsize=15,
            pad=12,
            loc="left",
        )
        panel_b.grid(True, which="major", color=GRID, lw=0.6)
        panel_b.axvline(
            checkpoints[0, 2],
            color=FOREGROUND,
            lw=0.8,
            alpha=0.5,
            ls=":",
            label="sieve checkpoints start here (primes of 10⁹)",
        )
        panel_b.legend(
            loc="upper left",
            frameon=True,
            facecolor=BACKGROUND,
            edgecolor=GRID,
            fontsize=10.8,
        )

        # inset: the two decades of checkpoints, linear scale; every figure computed
        inset = panel_b.inset_axes([0.585, 0.07, 0.395, 0.335])
        inset.set_facecolor(BACKGROUND)
        from_1e9 = sizes >= 1e9
        lead_1e9 = checkpoints[0, 1]
        classical = lead_1e9 + np.array(
            [
                quad(classical_integrand, 1e9, size, limit=400)[0]
                for size in sizes[from_1e9]
            ]
        )
        power = lead_1e9 + constant * (
            digits_at_sizes[from_1e9] ** EXPONENT - checkpoints[0, 2] ** EXPONENT
        )
        inset.plot(
            digits_at_sizes[from_1e9], classical, color=THEORY, lw=1.8, ls=(0, (5, 3))
        )
        inset.plot(
            digits_at_sizes[from_1e9], power, color=POWER, lw=1.6, ls=(0, (1, 2))
        )
        inset.plot(
            checkpoints[:, 2],
            checkpoints[:, 1],
            color=CURVE,
            lw=0,
            marker="o",
            ms=5,
            mfc=BACKGROUND,
            mec=CURVE,
            mew=1.4,
        )
        inset.set_xscale("log")
        inset.set_xlim(1.9e8, 2.5e10)
        inset.set_ylim(150, 1300)
        inset.tick_params(labelsize=9)
        inset.grid(True, which="major", color=GRID, lw=0.5)
        for spine in inset.spines.values():
            spine.set_edgecolor(GRID)
        inset.set_title("the two decades of checkpoints", fontsize=10.5, pad=5)

        row = {
            int(x): (lead_value, digit_value)
            for x, lead_value, digit_value in checkpoints
        }
        rise_1 = row[10**10][0] - row[10**9][0]
        rise_2 = row[10**11][0] - row[10**10][0]
        classical_1 = quad(classical_integrand, 1e9, 1e10, limit=400)[0]
        classical_2 = quad(classical_integrand, 1e10, 1e11, limit=400)[0]
        power_1 = constant * (row[10**10][1] ** EXPONENT - row[10**9][1] ** EXPONENT)
        power_2 = constant * (row[10**11][1] ** EXPONENT - row[10**10][1] ** EXPONENT)
        log(
            f"rise of the lead, primes 1e9 to 1e10, then 1e10 to 1e11: measured "
            f"{rise_1:.2f} and {rise_2:.2f} ; classical {classical_1:.2f} and "
            f"{classical_2:.2f} ; fixed exponent {power_1:.2f} and {power_2:.2f}"
        )
        reference = {
            "measured": (
                r"R = rise of the lead from 1e9 to 1e10 = ([\d.]+)",
                r"R2 = rise of the lead from 1e10 to 1e11 = ([\d.]+)",
            ),
            "classical": (
                r"classical, no constant: C = ([\d.]+)",
                r"classical C2 = ([\d.]+)",
            ),
            "fixed exponent": (
                r"power law, ln2/ln3, A fixed: Pw = ([\d.]+)",
                r"power law Pw2 = ([\d.]+)",
            ),
        }
        computed = {
            "measured": (rise_1, rise_2),
            "classical": (classical_1, classical_2),
            "fixed exponent": (power_1, power_2),
        }
        for name, (first, second) in reference.items():
            there_1 = reference_value("step12_sieve_1e11.log", first)
            there_2 = reference_value("step12_sieve_1e11.log", second)
            log(
                f"   {name}: here {computed[name][0]:.2f} and {computed[name][1]:.2f} ; "
                f"in the 7 October sieve log {there_1:.2f} and {there_2:.2f}"
            )
        inset.text(
            0.04,
            0.95,
            "primes 10⁹ to 10¹⁰, then to 10¹¹:\n"
            f"lead rose by {rise_1:.0f} and {rise_2:.0f}\n"
            f"classical: {classical_1:.0f} and {classical_2:.0f}\n"
            f"fixed exponent: {power_1:.0f} and {power_2:.0f}",
            transform=inset.transAxes,
            ha="left",
            va="top",
            fontsize=9.5,
        )
        figure.suptitle(
            "Digit gaps in the 5-series and 7-series prime products: a beat between two staircases",
            fontsize=17,
            x=0.012,
            ha="left",
            y=0.985,
        )
        figure.text(
            0.012,
            0.012,
            "5-series: primes of the form 6k+5; 7-series: 6k+1. Lead measured at equal product size.\n"
            "The classical curve takes one starting value, the measured lead at primes of 10⁴, and fits nothing. "
            f"Scripts and data: commit {commit}, regenerated {date}.",
            fontsize=10.5,
            alpha=0.7,
        )
        figure.tight_layout(rect=(0, 0.045, 1, 0.955))
        IMAGES.mkdir(parents=True, exist_ok=True)
        figure.savefig(IMAGES / "chebyshev_beat.png", dpi=120)
        end_lead = lead_start + cumulative[-1]
        log(
            f"classical at 1e11 from the 1e4 start: {end_lead:.1f}, measured "
            f"{checkpoints[-1, 1]:.1f}, fixed exponent "
            f"{lead_start + constant * (digits_at_sizes[-1] ** EXPONENT - digits_start**EXPONENT):.1f}"
        )
        log("saved docs/img/chebyshev_beat.png")


if __name__ == "__main__":
    main()
