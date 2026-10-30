# The two figures on the demo page

`docs/img/chebyshev_beat.png` and `docs/img/chebyshev_zeros.png`, redrawn by the
scripts in this folder. Every number printed on a figure is computed by its
script and written to `logs/`; the footer of each figure names the commit of the
scripts and data that drew it. A script refuses to draw from a dirty tree.

The scripts are ported from a review of 7 October 2026 (Python 3.13.16, numpy
2.5.3, scipy 1.18.1, matplotlib 3.11.2, Linux). Nothing is claimed as new: the
effect is Chebyshev's bias (1853).

## Run order

From this folder, with `pip install -r requirements.txt`:

| step | script | what it does | time here |
|---|---|---|---|
| 1 | `python step4_big.py` | primes to 10⁹, the 6k+5 and 6k+1 series and their cumulative log₁₀ sums, written to `work/` (about 800 MB, about 3 GB of memory) | 10 s |
| 2 | `python step1_clusters.py` | the 13 synchronisation clusters, found by the cluster finder in `core.py` (primes to 1.5 × 10⁷); compares them with `data/reference_step1_reproduce.log` | 0.2 s |
| 3 | `python step18_curve.py` | the lead from 10¹¹ to 10¹², measured (`data/p11_segments.npy`) and rebuilt (`recon.py` and `data/zeros_chi3_T3000.npy`), to `work/p11_curve.npy`; starting values read from `data/step12_sieve_1e11.log` | 11 s |
| 4 | `python fig_beat.py` | the first figure; fits the fixed-exponent constant A and prints it beside `data/reference_step11_powerlaw_vs_classical.log` | 3 s |
| 5 | `python fig_zeros.py` | the second figure; stops with a message if `work/p11_curve.npy` is missing | 11 s |

`work/` is not committed. `data/` is committed as filed: the zeros of
L(s, χ₋₃) below height 3000, the sieve of 10¹¹ to 10¹² in segments, the sieve log
to 10¹¹, and two logs of 7 October that the scripts compare against.

The sieve of 10¹¹ to 10¹² (81 minutes on 7 October) is not rerun here; its result is `data/p11_segments.npy`.

## The platform

These scripts sum logarithms in `np.longdouble`, which is 80-bit on Linux and
plain `float64` on Windows. The 7 October run was on Linux. This run was on
Windows 11 (build 10.0.26300), AMD Ryzen 5 PRO 7535U, 12 threads, 31 GB, Python
3.13.14, numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2, with `np.longdouble` at 64
bits. Each log's first line states which it was. Where the two runs can be
compared they agree: the 13 cluster centres, spans and edges are identical
(`logs/step1_clusters.log`), A is 0.15895 in both, and the measured, classical
and fixed-exponent rises to 10¹⁰ and 10¹¹ agree to the printed two decimals
(`logs/fig_beat.log`). A rerun here draws byte-identical PNGs.

## What changed from the 7 October scripts

Labels from the private review are removed. The four typed inputs are now
computed: A (fitted in `fig_beat.py`), the 13 centres (`step1_clusters.py`), the
starting counts at 10¹¹ (read from the sieve log), and the decade 10¹¹ to 10¹²
(the figure refuses to draw without it). `step18_curve.py` keeps only what
writes `p11_curve.npy`.
