"""Statistics needed by this study that stats.py (from kaf-w2s) does not provide.

Pure standard library, first-principles implementations, matching the style of stats.py.
"""
import math
import random


def pop_sd(xs):
    """Population standard deviation. Returns None for fewer than 2 values."""
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / n)


def _ranks(xs):
    """Average ranks with tie handling. Rank 1 = smallest."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j < len(order) and xs[order[j]] == xs[order[i]]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg
        i = j
    return ranks


def spearman(x, y):
    """Spearman rank correlation. Returns None if either side is constant."""
    if len(x) != len(y) or len(x) < 3:
        return None
    rx, ry = _ranks(x), _ranks(y)
    mx = sum(rx) / len(rx)
    my = sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def spearman_perm_p(x, y, sided="less", n_perm=10000, seed=42):
    """Permutation p-value for Spearman rho by shuffling y.

    sided="less": p = share of permutations with rho at or below the observed rho
    (the one-sided test for a negative correlation). sided="greater" mirrors it.
    Uses the add-one correction so p is never exactly zero.
    """
    obs = spearman(x, y)
    if obs is None:
        return None, None
    rng = random.Random(seed)
    yy = list(y)
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(yy)
        r = spearman(x, yy)
        if r is None:
            continue
        if sided == "less" and r <= obs:
            hits += 1
        elif sided == "greater" and r >= obs:
            hits += 1
    p = (hits + 1) / (n_perm + 1)
    return obs, p


def binom_test_greater(k, n, p=0.5):
    """Exact one-sided binomial test, P(X >= k) for X ~ Bin(n, p)."""
    if n == 0:
        return None
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return min(total, 1.0)


def quadratic_weighted_kappa(a, b, min_rating=1, max_rating=5):
    """Quadratic weighted kappa between two integer rating lists."""
    assert len(a) == len(b) and len(a) > 0
    k = max_rating - min_rating + 1
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[int(x) - min_rating][int(y) - min_rating] += 1
    n = len(a)
    hist_a = [sum(obs[i][j] for j in range(k)) for i in range(k)]
    hist_b = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    num = 0.0
    den = 0.0
    for i in range(k):
        for j in range(k):
            w = ((i - j) ** 2) / ((k - 1) ** 2)
            expected = hist_a[i] * hist_b[j] / n
            num += w * obs[i][j]
            den += w * expected
    if den == 0:
        return 1.0
    return 1.0 - num / den


def icc2_1(matrix):
    """ICC(2,1), two-way random effects, absolute agreement, single rater.

    matrix: list of rows, one row per item, one column per rater.
    """
    n = len(matrix)
    k = len(matrix[0]) if n else 0
    if n < 2 or k < 2:
        return None
    grand = sum(sum(row) for row in matrix) / (n * k)
    row_means = [sum(row) / k for row in matrix]
    col_means = [sum(matrix[i][j] for i in range(n)) / n for j in range(k)]
    ss_rows = k * sum((m - grand) ** 2 for m in row_means)
    ss_cols = n * sum((m - grand) ** 2 for m in col_means)
    ss_total = sum((matrix[i][j] - grand) ** 2 for i in range(n) for j in range(k))
    ss_err = ss_total - ss_rows - ss_cols
    ms_r = ss_rows / (n - 1)
    ms_c = ss_cols / (k - 1)
    ms_e = ss_err / ((n - 1) * (k - 1))
    denom = ms_r + (k - 1) * ms_e + k * (ms_c - ms_e) / n
    if denom == 0:
        return None
    return (ms_r - ms_e) / denom


def cosine_distance(u, v):
    dot = sum(a * b for a, b in zip(u, v))
    nu = math.sqrt(sum(a * a for a in u))
    nv = math.sqrt(sum(b * b for b in v))
    if nu == 0 or nv == 0:
        return None
    return 1.0 - dot / (nu * nv)


def mean_pairwise_cosine_distance(vectors):
    """Mean cosine distance over all pairs. Returns None with fewer than 2 vectors."""
    n = len(vectors)
    if n < 2:
        return None
    dists = []
    for i in range(n):
        for j in range(i + 1, n):
            d = cosine_distance(vectors[i], vectors[j])
            if d is not None:
                dists.append(d)
    if not dists:
        return None
    return sum(dists) / len(dists)


def minmax_normalize(values):
    """Min-max normalize a dict of numbers to [0, 1]. Constant input maps to 0.5."""
    vals = [v for v in values.values() if v is not None]
    if not vals:
        return {k: None for k in values}
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-12:
        return {k: (0.5 if v is not None else None) for k, v in values.items()}
    return {k: ((v - lo) / (hi - lo) if v is not None else None) for k, v in values.items()}
