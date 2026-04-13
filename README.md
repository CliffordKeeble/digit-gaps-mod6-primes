# Digit Gaps and Synchronisation Clusters in Mod-6 Prime Products

Cumulative products of primes from the two residue classes modulo 6 (the 5-series and 7-series) exhibit digit gaps -- decimal scales at which no product exists. This repository accompanies the paper analysing these gaps across four orders of magnitude in digit-length (up to 3.25 million digits), with null-model verification distinguishing prime-specific structure from generic properties of logarithmic sequences.

## What the paper finds

**Generic properties** (reproduced by random pseudo-primes with prime-number-theorem density): the spacing between coincident gaps lies in {1, 2, 3} for 99.9998% of 2.35 million spacings, with a distribution of approximately 68:26:6. These are properties of logarithmic accumulation, not of prime distribution.

**Prime-specific structure**: synchronisation clusters -- contiguous regions where both series gap at identical digits -- are fewer and larger for real primes than for random sequences (z = -2.04), and their spacing follows a power law with exponent beta = 0.637 +/- 0.029 (R^2 = 0.979), robust across all parameter choices. This exponent is numerically close to ln(2)/ln(3) = 0.6309; a derivation from prime-product considerations is an open question.

**What is not claimed**: no factoring attack is proposed. The paper demonstrates structural order in the multiplicative landscape of primes at all scales and argues this merits further investigation.

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
```

## Citation

Keeble, C. (2026). *Digit Gaps and Synchronisation Clusters in Mod-6 Prime Products: Analysis to 3.25 Million Digits with Null Model Verification.* Version 2.3.

Zenodo DOI: [pending upload]

## Author

Dr. Clifford Keeble, PhD -- ORCID: [0009-0003-6828-2155](https://orcid.org/0009-0003-6828-2155)

Woodbridge, UK
