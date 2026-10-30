# Digit Gaps and Synchronisation Clusters in Mod-6 Prime Products

Cumulative products of primes from the two residue classes modulo 6 (primes of the form 6k+5, and of the form 6k+1) step over some decimal lengths: "digit gaps". This repository holds the paper that measured them (v2.3, May 2026), its verification code and its null-model tests, as filed.

**Live demo:** https://cliffordkeeble.github.io/digit-gaps-mod6-primes/ — the two products computed exactly in your browser, in Python.

## What the digit gaps turned out to be

The paper's computations reproduce independently. Its interpretation has been superseded. The 6k+5 product runs slightly ahead of the 6k+1 product at nearly every size because primes of the form 6k+5 are slightly more common: **Chebyshev's bias**, observed in 1853. The paper's synchronisation clusters sit where that lead is a whole number of primes. Classical theory (the contribution of the squares of primes, plus the zeros of one L-function, L(s, χ₋₃)) rebuilds the lead's rise, with nothing fitted, from primes of 10⁴ to 10¹², to within 0.03 of a prime. The power-law exponent the paper measured is what the full classical formula, zeros included, gives over the measured range (0.634 ± 0.031, against the paper's 0.637 ± 0.029); its closeness to ln 2/ln 3 is not a mechanism.

**Already in print:** Chebyshev's bias and its explicit formula (Granville and Martin 2006; Bays, Ford, Hudson and Rubinstein 2001); predicting the mod 3 race from L-function zeros (Bays et al. 2001); which digit-lengths the ordinary primorial skips (OEIS A067175, A385863). A literature search with stated gaps did not find this particular view, two residue classes' products compared by digit-length, in print. **Nothing here is claimed as new.**

**What is not claimed:** no factoring attack, and no bearing on RSA or on post-quantum cryptography.

## Run the demo and its tests

Needs Python 3.11 or later and `pip install pytest`. `python -m pytest -q` runs the fast tests (a few seconds; `-m slow` adds the 10⁷ case). `python -m http.server -d docs`, then http://localhost:8000, serves the page locally; it loads Python from the jsDelivr CDN, so it needs internet access.

**Measured** (filled in after the page is live: date, device, browser, Python load and compute time at 10⁶): desktop …; phone ….

## Reproduce in 32 seconds

```bash
git clone https://github.com/cliffordkeeble/digit-gaps-mod6-primes.git
cd digit-gaps-mod6-primes
python3 verification/full_null_model.py
```

Requires only Python 3 standard library. No external dependencies. Sieves primes to 15,000,000, computes cumulative log10 products for both series, verifies all spacing statistics, runs 10 null-model trials, performs cluster detection with sensitivity analysis, and reports all comparisons.

## Repository layout

```
paper/                  Paper (PDF + markdown, v2.3)
verification/           Reproduction script + log
  full_null_model.py    Self-contained verification (std lib only)
  reproduction_log.md   Run output compared to paper claims
null-tests/             New null-model tests for pending observations
  phase_transition_null.py   Section 4.2 staggered-to-coincident transition
  jump_pair_null.py          Section 5.3 JUMP/PAIR heartbeat
  results/                   Raw outputs
findings.md             Top-level verification and null-test write-up
docs/                   The live demo page (GitHub Pages)
tests/                  pytest for the page's Python
figures/chebyshev/      The two figures and the scripts that draw them
```

## Citation

Keeble, C. (2026). *Digit Gaps and Synchronisation Clusters in Mod-6 Prime Products: Analysis to 3.25 Million Digits with Null Model Verification.* Version 2.3.

Zenodo DOI: [pending upload]

## Author

Dr. Clifford Keeble, PhD -- ORCID: [0009-0003-6828-2155](https://orcid.org/0009-0003-6828-2155)

Woodbridge, UK
