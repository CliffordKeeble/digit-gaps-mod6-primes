#!/usr/bin/env python3
"""
Table Generation for Paper A v3.6 (Sections 4-5)
=================================================

Computes and emits three tables for the digit-gaps-mod6-primes paper:
  Table 1: Digit counts/log10 for Pi_5(n), Pi_7(n), n=28..32 (10^61 gap)
  Table 2: Digit counts/log10 for Pi_5(n), Pi_7(n), n=36..40 (10^80 gap)
  Table 3: Modular residues supporting Theorems 5 and 6

Uses mpmath at 200-digit precision throughout.
Outputs to stdout and to boundary/tables_for_v3_6.md.
"""
import sys
import os
import mpmath

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

mpmath.mp.dps = 200  # 200 decimal digits


def sieve(limit):
    """Simple sieve of Eratosthenes."""
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def get_mod6_primes(primes):
    """Separate primes into 5-series (p mod 6 = 5) and 7-series (p mod 6 = 1)."""
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    return p5, p7


def compute_products_and_logs(prime_list, max_n):
    """Compute cumulative products Pi(n) = p_1 * p_2 * ... * p_n using mpmath.

    Returns lists of (product_as_int, digit_count, log10_value, prime_used)
    for n = 1..max_n.
    """
    results = []
    prod = mpmath.mpf(1)
    for i in range(max_n):
        p = prime_list[i]
        prod *= p
        prod_int = int(prod)
        # Digit count via string length of exact integer product
        # (we also compute via mpmath product separately for log10)
        digit_count = len(str(prod_int))
        log10_val = mpmath.log10(prod)
        results.append((prod_int, digit_count, log10_val, p))
    return results


def compute_exact_products(prime_list, max_n):
    """Compute cumulative products using exact Python integers.

    Returns list of (product, digit_count, prime_used) for n = 1..max_n.
    """
    results = []
    prod = 1
    for i in range(max_n):
        p = prime_list[i]
        prod *= p
        digit_count = len(str(prod))
        results.append((prod, digit_count, p))
    return results


def format_log10(val, decimals=4):
    """Format an mpmath log10 value to given decimal places."""
    return mpmath.nstr(val, decimals + 2, strip_zeros=False)


def table_1(p5_results, p7_results):
    """Table 1: n=28..32, showing the 10^61 digit gap."""
    lines = []
    lines.append("### Table 1 — Digit counts across the 10^61 gap (n = 28 to 32)")
    lines.append("")
    lines.append("| n | D_5(n) | log10 Pi_5(n) | p_{5,n} | D_7(n) | log10 Pi_7(n) | p_{7,n} |")
    lines.append("|--:|-------:|--------------:|--------:|-------:|--------------:|--------:|")

    for n in range(28, 33):  # 28..32
        idx = n - 1  # 0-indexed
        _, d5, log5, p5 = p5_results[idx]
        _, d7, log7, p7 = p7_results[idx]
        log5_str = format_log10(log5, 4)
        log7_str = format_log10(log7, 4)
        lines.append(f"| {n} | {d5} | {log5_str} | {p5} | {d7} | {log7_str} | {p7} |")

    return "\n".join(lines)


def table_2(p5_results, p7_results):
    """Table 2: n=36..40, showing the coincident 10^80 gap."""
    lines = []
    lines.append("### Table 2 — Digit counts across the coincident 10^80 gap (n = 36 to 40)")
    lines.append("")
    lines.append("| n | D_5(n) | log10 Pi_5(n) | p_{5,n} | D_7(n) | log10 Pi_7(n) | p_{7,n} |")
    lines.append("|--:|-------:|--------------:|--------:|-------:|--------------:|--------:|")

    for n in range(36, 41):  # 36..40
        idx = n - 1  # 0-indexed
        _, d5, log5, p5 = p5_results[idx]
        _, d7, log7, p7 = p7_results[idx]
        log5_str = format_log10(log5, 4)
        log7_str = format_log10(log7, 4)
        lines.append(f"| {n} | {d5} | {log5_str} | {p5} | {d7} | {log7_str} | {p7} |")

    return "\n".join(lines)


def table_3(p5_exact, p7_exact):
    """Table 3: Modular residues for Theorems 5 and 6."""
    # Pi_5(38) = product of first 38 primes in 5-series
    pi5_38 = p5_exact[37][0]  # 0-indexed
    # Pi_7(37) = product of first 37 primes in 7-series
    pi7_37 = p7_exact[36][0]  # 0-indexed

    pi5_38_mod3 = pi5_38 % 3
    pi5_38_mod5 = pi5_38 % 5
    pi7_37_mod3 = pi7_37 % 3
    pi7_37_mod5 = pi7_37 % 5
    pi7_37_mod15 = pi7_37 % 15

    lines = []
    lines.append("### Table 3 — Modular residues (Theorems 5 and 6)")
    lines.append("")
    lines.append("| Quantity | Value |")
    lines.append("|:---------|------:|")
    lines.append(f"| Pi_5(38) mod 3 | {pi5_38_mod3} |")
    lines.append(f"| Pi_5(38) mod 5 | {pi5_38_mod5} |")
    lines.append(f"| Pi_7(37) mod 3 | {pi7_37_mod3} |")
    lines.append(f"| Pi_7(37) mod 5 | {pi7_37_mod5} |")
    lines.append(f"| Pi_7(37) mod 15 | {pi7_37_mod15} |")

    return lines, {
        'pi5_38_mod3': pi5_38_mod3,
        'pi5_38_mod5': pi5_38_mod5,
        'pi7_37_mod3': pi7_37_mod3,
        'pi7_37_mod5': pi7_37_mod5,
        'pi7_37_mod15': pi7_37_mod15,
    }


def cross_check(p5_results, p7_results, residues):
    """Cross-check computed values against paper claims."""
    lines = []
    lines.append("### Cross-check notes")
    lines.append("")

    issues = []

    # Table 1 checks: D_5(30)=59, D_5(31)=62, D_7(30)=61, D_7(31)=64
    d5_30 = p5_results[29][1]
    d5_31 = p5_results[30][1]
    d7_30 = p7_results[29][1]
    d7_31 = p7_results[30][1]

    checks_t1 = [
        ("D_5(30)", d5_30, 59),
        ("D_5(31)", d5_31, 62),
        ("D_7(30)", d7_30, 61),
        ("D_7(31)", d7_31, 64),
    ]
    for name, got, expected in checks_t1:
        if got != expected:
            issues.append(f"FLAG: {name} = {got}, expected {expected}")

    # Table 2 checks: D_5(38)=79, D_5(39)=82, D_7(37)=79, D_7(38)=82
    d5_38 = p5_results[37][1]
    d5_39 = p5_results[38][1]
    d7_37 = p7_results[36][1]
    d7_38 = p7_results[37][1]

    checks_t2 = [
        ("D_5(38)", d5_38, 79),
        ("D_5(39)", d5_39, 82),
        ("D_7(37)", d7_37, 79),
        ("D_7(38)", d7_38, 82),
    ]
    for name, got, expected in checks_t2:
        if got != expected:
            issues.append(f"FLAG: {name} = {got}, expected {expected}")

    # Table 3 checks
    if residues['pi5_38_mod5'] != 0:
        issues.append(f"FLAG: Pi_5(38) mod 5 = {residues['pi5_38_mod5']}, expected 0 (since 5 in P_5)")
    if residues['pi7_37_mod3'] != 1:
        issues.append(f"FLAG: Pi_7(37) mod 3 = {residues['pi7_37_mod3']}, expected 1 (Lemma 3)")
    if residues['pi7_37_mod5'] != 2:
        issues.append(f"FLAG: Pi_7(37) mod 5 = {residues['pi7_37_mod5']}, expected 2 (Theorem 6)")
    # CRT check: if x ≡ 1 (mod 3) and x ≡ 2 (mod 5), then x ≡ 7 (mod 15).
    # The brief expected 2, but CRT(1 mod 3, 2 mod 5) = 7 mod 15.
    # We check consistency with the individual residues instead.
    expected_mod15 = None
    if residues['pi7_37_mod3'] is not None and residues['pi7_37_mod5'] is not None:
        # Solve via CRT: find x in [0,15) with x ≡ a (mod 3), x ≡ b (mod 5)
        a, b = residues['pi7_37_mod3'], residues['pi7_37_mod5']
        for x in range(15):
            if x % 3 == a and x % 5 == b:
                expected_mod15 = x
                break
    if expected_mod15 is not None and residues['pi7_37_mod15'] != expected_mod15:
        issues.append(f"FLAG: Pi_7(37) mod 15 = {residues['pi7_37_mod15']}, "
                      f"expected {expected_mod15} (CRT from mod 3 = {a}, mod 5 = {b})")
    if residues['pi5_38_mod3'] != 1:
        issues.append(f"FLAG: Pi_5(38) mod 3 = {residues['pi5_38_mod3']}, expected 1 (2^38 mod 3 = 1)")

    if issues:
        lines.append("**Issues found:**")
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("All computed values match the theorems' stated values in v3.6 sections 4-5.")
        lines.append("Table 1 digit gaps at {60, 61} for 5-series and {62, 63} for 7-series confirmed.")
        lines.append("Table 2 coincident gap at {80, 81} for both series confirmed.")
        lines.append("Table 3 residues consistent with Theorems 5, 6, and Lemma 3.")

    return "\n".join(lines), len(issues) == 0


def main():
    print("=" * 72)
    print("TABLE GENERATION FOR PAPER A v3.6")
    print(f"mpmath precision: {mpmath.mp.dps} decimal digits")
    print("=" * 72)

    # Sieve primes up to a comfortable margin
    primes = sieve(500_000)
    p5_list, p7_list = get_mod6_primes(primes)

    # Verify we have enough primes
    assert len(p5_list) >= 40, f"Need 40 primes in 5-series, got {len(p5_list)}"
    assert len(p7_list) >= 40, f"Need 40 primes in 7-series, got {len(p7_list)}"

    # Print first 40 of each series for verification
    print(f"\nFirst 40 primes of 5-series (p mod 6 = 5):")
    print(f"  {p5_list[:40]}")
    print(f"\nFirst 40 primes of 7-series (p mod 6 = 1):")
    print(f"  {p7_list[:40]}")

    # Verify known primes in each series
    expected_p5 = [5, 11, 17, 23, 29, 41, 47, 53, 59, 71]
    expected_p7 = [7, 13, 19, 31, 37, 43, 61, 67, 73, 79]
    assert p5_list[:10] == expected_p5, f"5-series mismatch: {p5_list[:10]} != {expected_p5}"
    assert p7_list[:10] == expected_p7, f"7-series mismatch: {p7_list[:10]} != {expected_p7}"
    print("\nPrime verification: first 10 of each series match expected values.")

    # Compute products using mpmath (for log10 values)
    print("\nComputing cumulative products with mpmath...")
    p5_results = compute_products_and_logs(p5_list, 40)
    p7_results = compute_products_and_logs(p7_list, 40)

    # Compute exact integer products (for modular arithmetic)
    print("Computing exact integer products...")
    p5_exact = compute_exact_products(p5_list, 40)
    p7_exact = compute_exact_products(p7_list, 40)

    # Cross-check digit counts between mpmath and exact methods
    for n in range(40):
        assert p5_results[n][1] == p5_exact[n][1], \
            f"5-series digit count mismatch at n={n+1}: {p5_results[n][1]} vs {p5_exact[n][1]}"
        assert p7_results[n][1] == p7_exact[n][1], \
            f"7-series digit count mismatch at n={n+1}: {p7_results[n][1]} vs {p7_exact[n][1]}"
    print("Digit count cross-check (mpmath vs exact int): all 80 values agree.")

    # Generate tables
    t1 = table_1(p5_results, p7_results)
    t2 = table_2(p5_results, p7_results)
    t3_lines, residues = table_3(p5_exact, p7_exact)
    t3 = "\n".join(t3_lines)
    cross, all_ok = cross_check(p5_results, p7_results, residues)

    # Print to stdout
    print("\n" + "=" * 72)
    print(t1)
    print()
    print(t2)
    print()
    print(t3)
    print()
    print(cross)
    print("=" * 72)

    # Write to file
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "tables_for_v3_6.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Tables for Paper A v3.6\n\n")
        f.write(f"Generated by `boundary/table_generation.py` at mpmath "
                f"precision {mpmath.mp.dps} digits.\n\n")
        f.write("---\n\n")
        f.write(t1 + "\n\n")
        f.write(t2 + "\n\n")
        f.write(t3 + "\n\n")
        f.write("---\n\n")
        f.write(cross + "\n")

    print(f"\nTables written to {output_path}")

    if not all_ok:
        print("\n*** FLAGS FOUND — see cross-check notes above ***")
        sys.exit(1)
    else:
        print("\nAll cross-checks passed.")


if __name__ == "__main__":
    main()
