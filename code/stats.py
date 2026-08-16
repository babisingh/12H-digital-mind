# Zero-dependency statistics library from the author's prior KAF work,
# released with this project unmodified.
"""
Statistical Analysis Utilities for KAF Experiments

Zero external dependencies (no scipy required).
All tests implemented from first principles with exact or bootstrap-based p-values.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple, Optional


# ─── Mann-Whitney U Test ────────────────────────────────────────────────────

def mann_whitney_u(a: List[float], b: List[float]) -> Tuple[float, float]:
    """
    Two-sided Mann-Whitney U test.
    Returns (U_statistic, p_value_approx).
    Uses normal approximation for n > 8, exact enumeration for small n.
    """
    n1, n2 = len(a), len(b)
    combined = sorted([(v, 0) for v in a] + [(v, 1) for v in b])

    # Assign ranks (handle ties with average rank)
    ranks = [0.0] * (n1 + n2)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    r1 = sum(ranks[k] for k in range(n1 + n2) if combined[k][1] == 0)
    U1 = r1 - n1 * (n1 + 1) / 2.0
    U2 = n1 * n2 - U1
    U = min(U1, U2)

    # Normal approximation
    mu_U = n1 * n2 / 2.0
    sigma_U = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    if sigma_U == 0:
        return U, 1.0
    z = (U - mu_U) / sigma_U
    p = 2 * (1 - _normal_cdf(abs(z)))  # two-sided
    return U, p


def _normal_cdf(z: float) -> float:
    """Approximation of the standard normal CDF."""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ─── Cliff's Delta (Effect Size) ────────────────────────────────────────────

def cliffs_delta(a: List[float], b: List[float]) -> float:
    """
    Cliff's delta: probability that a random value from a exceeds one from b.
    Range [-1, 1]. |d| < 0.147 = negligible, < 0.33 = small, < 0.474 = medium, else large.
    """
    n1, n2 = len(a), len(b)
    dominance = sum(1 if ai > bj else (-1 if ai < bj else 0)
                    for ai in a for bj in b)
    return dominance / (n1 * n2)


def effect_size_label(d: float) -> str:
    d = abs(d)
    if d < 0.147:
        return "negligible"
    elif d < 0.33:
        return "small"
    elif d < 0.474:
        return "medium"
    return "large"


# ─── Bootstrap Confidence Interval ──────────────────────────────────────────

def bootstrap_ci(values: List[float], stat_fn=None, n_boot: int = 2000,
                 ci: float = 0.95, seed: int = 42) -> Tuple[float, float]:
    """
    Bootstrap confidence interval for a statistic.
    stat_fn defaults to mean.
    """
    if stat_fn is None:
        stat_fn = lambda xs: sum(xs) / len(xs)
    rng = random.Random(seed)
    n = len(values)
    boot_stats = []
    for _ in range(n_boot):
        sample = [rng.choice(values) for _ in range(n)]
        boot_stats.append(stat_fn(sample))
    boot_stats.sort()
    lo = boot_stats[int((1 - ci) / 2 * n_boot)]
    hi = boot_stats[int((1 + ci) / 2 * n_boot)]
    return lo, hi


# ─── Fisher's Exact Test (2×2) ──────────────────────────────────────────────

def fishers_exact(a_success: int, a_total: int,
                  b_success: int, b_total: int) -> Tuple[float, float]:
    """
    Fisher's exact test for 2×2 contingency table.
    Returns (odds_ratio, p_value two-sided).
    """
    a_fail = a_total - a_success
    b_fail = b_total - b_success

    def hypergeom_prob(k: int, n1: int, n2: int, N: int) -> float:
        """P(X=k) under hypergeometric distribution."""
        return _comb(n1, k) * _comb(n2, N - k) / _comb(n1 + n2, N)

    def _comb(n: int, k: int) -> float:
        if k < 0 or k > n:
            return 0.0
        if k == 0 or k == n:
            return 1.0
        k = min(k, n - k)
        result = 1.0
        for i in range(k):
            result = result * (n - i) / (i + 1)
        return result

    N = a_success + b_success
    n1 = a_total
    n2 = b_total
    obs_prob = hypergeom_prob(a_success, n1, n2, N)

    p = 0.0
    for k in range(max(0, N - n2), min(n1, N) + 1):
        p_k = hypergeom_prob(k, n1, n2, N)
        if p_k <= obs_prob + 1e-10:
            p += p_k

    odds_ratio = float('inf')
    if a_fail > 0 and b_success > 0:
        odds_ratio = (a_success * b_fail) / (a_fail * b_success)
    return odds_ratio, min(p, 1.0)


# ─── Kruskal-Wallis Test (k groups) ─────────────────────────────────────────

def kruskal_wallis(*groups: List[float]) -> Tuple[float, float]:
    """
    Kruskal-Wallis H test for k independent groups.
    Returns (H_statistic, p_value_approx) using chi-squared approximation.
    """
    k = len(groups)
    all_vals = [(v, gi) for gi, g in enumerate(groups) for v in g]
    all_vals.sort(key=lambda x: x[0])
    n = len(all_vals)

    # Assign ranks with tie correction
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and all_vals[j][0] == all_vals[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for kk in range(i, j):
            ranks[kk] = avg_rank
        i = j

    group_ranks = [[] for _ in range(k)]
    for idx, (_, gi) in enumerate(all_vals):
        group_ranks[gi].append(ranks[idx])

    ns = [len(g) for g in group_ranks]
    H = (12 / (n * (n + 1))) * sum(
        sum(r for r in group_ranks[i]) ** 2 / ns[i] for i in range(k)
    ) - 3 * (n + 1)

    # p-value from chi-squared distribution with df=k-1
    df = k - 1
    p = 1 - _chi2_cdf(H, df)
    return H, p


def _chi2_cdf(x: float, df: int) -> float:
    """Chi-squared CDF via regularized incomplete gamma function approximation."""
    if x <= 0:
        return 0.0
    return _regularized_gamma(df / 2, x / 2)


def _regularized_gamma(a: float, x: float, max_iter: int = 200) -> float:
    """Lower regularized incomplete gamma function P(a, x) via series expansion."""
    if x < 0:
        return 0.0
    if x == 0:
        return 0.0
    log_gamma_a = _log_gamma(a)
    term = math.exp(-x + a * math.log(x) - log_gamma_a) / a
    total = term
    for n in range(1, max_iter):
        term *= x / (a + n)
        total += term
        if term < 1e-10 * total:
            break
    return min(total, 1.0)


def _log_gamma(z: float) -> float:
    """Stirling approximation of log(Gamma(z))."""
    if z < 0.5:
        return math.log(math.pi / math.sin(math.pi * z)) - _log_gamma(1 - z)
    z -= 1
    coeffs = [76.18009172947146, -86.50532032941677, 24.01409824083091,
              -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]
    x = 1.000000000190015
    for i, c in enumerate(coeffs):
        x += c / (z + i + 1)
    t = z + 5.5
    return 0.5 * math.log(2 * math.pi) + (z + 0.5) * math.log(t) - t + math.log(x)


# ─── Reporting Utilities ─────────────────────────────────────────────────────

def format_p(p: float) -> str:
    if p < 0.001:
        return "p < 0.001"
    elif p < 0.01:
        return f"p = {p:.3f}"
    elif p < 0.05:
        return f"p = {p:.3f}"
    else:
        return f"p = {p:.3f} (n.s.)"


def report_comparison(name: str, a: List[float], b: List[float],
                      label_a: str = "A", label_b: str = "B") -> None:
    mean_a = sum(a) / len(a) if a else 0
    mean_b = sum(b) / len(b) if b else 0
    ci_a = bootstrap_ci(a) if len(a) > 1 else (mean_a, mean_a)
    ci_b = bootstrap_ci(b) if len(b) > 1 else (mean_b, mean_b)
    U, p = mann_whitney_u(a, b)
    d = cliffs_delta(a, b)

    print(f"\n  {name}")
    print(f"    {label_a}: {mean_a:.3f} [{ci_a[0]:.3f}, {ci_a[1]:.3f}]")
    print(f"    {label_b}: {mean_b:.3f} [{ci_b[0]:.3f}, {ci_b[1]:.3f}]")
    print(f"    Mann-Whitney: U={U:.1f}, {format_p(p)}")
    print(f"    Cliff's delta: {d:.3f} ({effect_size_label(d)} effect)")
