import ast
import random
import re
import sys
from pathlib import Path

import chebyshev_race
import pytest
from chebyshev_race import (
    ALLOWED_BOUNDS,
    RESULT_KEYS,
    TRAP_KEYS,
    _correct_digit_estimate,
    digit_count,
    float_trap,
    primes_upto,
    product_tree,
    race,
)

# bound: (count 5 mod 6, count 1 mod 6, digits 5 mod 6, digits 1 mod 6, pi(bound))
# Computed on 29 Oct 2026, exact route. At 10^5 and 10^6 also by
# len(str()) and by math.fsum of log10 p: all three equal.
GOLDEN = {
    10**5: (4806, 4784, 21685, 21608, 9592),
    10**6: (39265, 39231, 216876, 216760, 78498),
    10**7: (332383, 332194, 2170970, 2169881, 664579),
}


@pytest.fixture(autouse=True, scope="module")
def unlimited_str_digits():
    """Reading the truth with len(str(n)) needs the int-to-str limit off."""
    previous = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(0)
    yield
    sys.set_int_max_str_digits(previous)


def test_primes_upto_small_bounds():
    assert primes_upto(-5) == []
    assert primes_upto(0) == []
    assert primes_upto(1) == []
    assert primes_upto(2) == [2]
    assert primes_upto(3) == [2, 3]
    assert primes_upto(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


def test_primes_upto_counts():
    assert len(primes_upto(10**5)) == 9592
    assert len(primes_upto(10**6)) == 78498


def test_digit_count_at_boundaries_equals_len_of_str():
    for exponent in range(1, 3001):
        for n in (
            10**exponent - 1,
            10**exponent,
            10**exponent + 1,
            2**exponent - 1,
            2**exponent,
        ):
            assert digit_count(n) == len(str(n)), (exponent, n.bit_length())


def test_digit_count_on_random_integers():
    rng = random.Random(2026)
    for _ in range(200):
        n = rng.getrandbits(rng.randint(1, 100_000)) or 1
        assert digit_count(n) == len(str(n))


def test_digit_count_refuses_non_positive():
    with pytest.raises(ValueError):
        digit_count(0)
    with pytest.raises(ValueError):
        digit_count(-7)


def test_correct_digit_estimate_moves_both_ways():
    """The boundary sweep cannot reach a float that rounds up across an integer
    (that needs millions of bits), so test the downward branch directly."""
    for exponent in (1, 2, 3, 9, 10, 17, 18, 100, 1000):
        for n in (10**exponent - 1, 10**exponent, 10**exponent + 1):
            true_count = len(str(n))
            for estimate in (true_count - 1, true_count, true_count + 1):
                assert _correct_digit_estimate(n, estimate) == true_count, (
                    n,
                    estimate,
                )


@pytest.mark.parametrize("bound", [10**5, 10**6])
def test_race_matches_golden_values(bound):
    count_5, count_1, digits_5, digits_1, pi_of_bound = GOLDEN[bound]
    result = race(bound)
    assert result["count_5_mod_6"] == count_5
    assert result["count_1_mod_6"] == count_1
    assert result["digits_5_mod_6"] == digits_5
    assert result["digits_1_mod_6"] == digits_1
    assert result["digit_difference"] == digits_5 - digits_1
    assert result["larger"] == "5 mod 6"
    # The independent check: the 2 is the primes 2 and 3.
    assert result["count_5_mod_6"] + result["count_1_mod_6"] + 2 == pi_of_bound


@pytest.mark.slow
def test_race_matches_golden_values_at_ten_million():
    count_5, count_1, digits_5, digits_1, pi_of_bound = GOLDEN[10**7]
    result = race(10**7)
    assert result["count_5_mod_6"] == count_5
    assert result["count_1_mod_6"] == count_1
    assert result["digits_5_mod_6"] == digits_5
    assert result["digits_1_mod_6"] == digits_1
    assert result["count_5_mod_6"] + result["count_1_mod_6"] + 2 == pi_of_bound


def test_race_digits_agree_with_len_of_str_at_100000():
    primes = primes_upto(10**5)
    product_5 = product_tree([prime for prime in primes if prime % 6 == 5])
    product_1 = product_tree([prime for prime in primes if prime % 6 == 1])
    result = race(10**5)
    assert result["digits_5_mod_6"] == len(str(product_5))
    assert result["digits_1_mod_6"] == len(str(product_1))


def test_race_keys_equal_result_keys():
    result = race(10**5)
    assert tuple(result) == RESULT_KEYS
    assert result["bound"] == 10**5
    for key in RESULT_KEYS:
        if key.startswith("seconds_"):
            assert result[key] >= 0


@pytest.mark.parametrize(
    "bound", [999, -1, 0, 10**5 + 1, 3 * 10**6, 10**8, 1.5e6, 1e6, True, "1000000"]
)
def test_race_refuses_bounds_not_allowed(bound):
    with pytest.raises(ValueError):
        race(bound)


def test_allowed_bounds():
    assert ALLOWED_BOUNDS == (10**5, 10**6, 2 * 10**6, 5 * 10**6, 10**7)


def running_product(factors):
    product = 1
    for factor in factors:
        product *= factor
    return product


@pytest.mark.parametrize("length", [0, 1, 2, 3])
def test_product_tree_matches_running_product_for_short_lists(length):
    factors = [3, 5, 7][:length]
    assert product_tree(factors) == running_product(factors)


def test_product_tree_of_nothing_is_one():
    assert product_tree([]) == 1


def test_product_tree_matches_running_product_for_primes_to_1000():
    primes = primes_upto(1000)
    assert product_tree(primes) == running_product(primes)
    for length in (4, 5, 6, 7, 8, 9, 100):
        assert product_tree(primes[:length]) == running_product(primes[:length])


def test_float_trap_is_platform_independent():
    """10**61 is not a double (5**61 needs more than 53 bits), so the float
    route cannot equal it, and fewer than 17 leading digits agree. The
    remainder mod 3 depends on the platform's exp, so it is not pinned."""
    trap = float_trap()
    assert tuple(trap) == TRAP_KEYS
    assert trap["exact"] == "1" + "0" * 61
    assert trap["exact_digits"] == 62
    assert trap["float_route"] != trap["exact"]
    assert trap["leading_digits_agree"] < 17
    assert int(trap["exact"]) - int(trap["float_route"]) == int(trap["difference"])
    assert trap["exact_mod_3"] == 1
    assert trap["float_mod_3"] in (0, 1, 2)
    for key in ("float_route", "exact", "difference"):
        assert isinstance(trap[key], str)


DOCS = Path(__file__).resolve().parent.parent / "docs"


def keys_listed_in_app_js(constant_name):
    source = (DOCS / "app.js").read_text(encoding="utf-8")
    match = re.search(rf"const {constant_name} = \[(.*?)\];", source, re.DOTALL)
    assert match, f"app.js has no `const {constant_name} = [...]`"
    return tuple(re.findall(r'"([^"]+)"', match.group(1)))


def test_app_js_reads_the_keys_the_module_returns():
    assert keys_listed_in_app_js("RESULT_KEYS") == RESULT_KEYS
    assert keys_listed_in_app_js("TRAP_KEYS") == TRAP_KEYS


def test_every_result_key_is_used_by_the_page():
    app_source = (DOCS / "app.js").read_text(encoding="utf-8")
    html_source = (DOCS / "index.html").read_text(encoding="utf-8")
    for key in RESULT_KEYS:
        if key in ("bound", "seconds_sieve", "seconds_multiply", "seconds_digit_count"):
            continue  # carried in the reply; not shown as such
        assert key in app_source or f'data-field="{key}"' in html_source, key


def test_worker_pins_pyodide_and_never_a_moving_version():
    worker_source = (DOCS / "worker.js").read_text(encoding="utf-8")
    assert 'PYODIDE_VERSION = "314.0.7"' in worker_source
    for moving in ("/latest/", "/dev/", "@latest"):
        assert moving not in worker_source


def test_pages_serves_the_files_as_committed():
    assert (DOCS / ".nojekyll").is_file()


def test_module_is_standard_library_only():
    allowed = {"itertools", "math", "time", "collections"}
    tree = ast.parse(Path(chebyshev_race.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module.split(".")[0])
    assert imported <= allowed, imported - allowed
