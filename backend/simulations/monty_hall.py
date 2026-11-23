import numpy as np


def simulate(trials: int, seed: int | None = None) -> dict:
    rng = np.random.default_rng(seed)

    prize = rng.integers(0, 3, size=trials)
    first_pick = rng.integers(0, 3, size=trials)

    stay_wins = first_pick == prize
    switch_wins = ~stay_wins

    stay_freq = np.cumsum(stay_wins) / np.arange(1, trials + 1)
    switch_freq = np.cumsum(switch_wins) / np.arange(1, trials + 1)

    return {
        "theoretical": {"stay": 1 / 3, "switch": 2 / 3},
        "simulated": {
            "stay": float(stay_freq[-1]),
            "switch": float(switch_freq[-1]),
        },
        "convergence": [
            {
                "trial": t,
                "stay": float(s),
                "switch": float(w),
            }
            for t, s, w in _paired_downsample(stay_freq, switch_freq)
        ],
    }


def _paired_downsample(a: np.ndarray, b: np.ndarray, points: int = 200):
    n = len(a)
    if n <= points:
        return list(zip(range(1, n + 1), a, b))
    idx = np.linspace(0, n - 1, points, dtype=int)
    return [(int(i) + 1, a[i], b[i]) for i in idx]
