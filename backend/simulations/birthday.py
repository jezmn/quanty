import numpy as np

DAYS = 365


def theoretical_at_least_two_shared(n: int) -> float:
    if n <= 1:
        return 0.0
    p_all_distinct = 1.0
    for i in range(n):
        p_all_distinct *= (DAYS - i) / DAYS
    return 1.0 - p_all_distinct


def theoretical_curve(max_people: int = 60) -> list[dict]:
    return [
        {"n": n, "p": theoretical_at_least_two_shared(n)}
        for n in range(1, max_people + 1)
    ]


def simulate(n: int, trials: int, seed: int | None = None) -> dict:
    rng = np.random.default_rng(seed)
    days = rng.integers(0, DAYS, size=(trials, n))
    if n > 1:
        ordered = np.sort(days, axis=1)
        matches = np.any(np.diff(ordered, axis=1) == 0, axis=1)
    else:
        matches = np.zeros(trials, dtype=bool)
    hits = np.cumsum(matches)
    running_estimates = hits / np.arange(1, trials + 1)
    return {
        "theoretical": theoretical_at_least_two_shared(n),
        "simulated": float(running_estimates[-1]),
        "convergence": [
            {"trial": t, "estimate": float(e)}
            for t, e in _downsample(running_estimates)
        ],
        "groups_shared": int(hits[-1]),
        "groups_total": trials,
    }


def _downsample(values: np.ndarray, points: int = 200) -> list[tuple[int, float]]:
    n = len(values)
    if n <= points:
        return list(enumerate(values, start=1))
    idx = np.linspace(0, n - 1, points, dtype=int)
    return [(int(i) + 1, float(values[i])) for i in idx]
