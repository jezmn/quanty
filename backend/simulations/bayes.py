import numpy as np


def theoretical(p_prev: float, p_sens: float, p_false_pos: float) -> float:
    p_true_pos = p_sens * p_prev
    p_false_pos = p_false_pos * (1 - p_prev)
    if p_true_pos + p_false_pos == 0:
        return 0.0
    return p_true_pos / (p_true_pos + p_false_pos)


def simulate(
    p_prev: float,
    p_sens: float,
    p_false_pos: float,
    population: int,
    seed: int | None = None,
) -> dict:
    rng = np.random.default_rng(seed)

    sick = rng.random(population) < p_prev
    positive = np.where(sick, rng.random(population) < p_sens,
                        rng.random(population) < p_false_pos)

    is_tp = positive & sick
    is_fp = positive & ~sick

    positives = np.cumsum(positive)
    true_pos = np.cumsum(is_tp)
    posterior_running = true_pos / np.maximum(positives, 1)

    return {
        "theoretical": theoretical(p_prev, p_sens, p_false_pos),
        "simulated": float(posterior_running[-1]),
        "convergence": [
            {"trial": t, "estimate": float(e)}
            for t, e in _downsample(posterior_running)
        ],
        "population": {
            "sick_positive": int(is_tp.sum()),
            "sick_negative": int((sick & ~positive).sum()),
            "healthy_positive": int(is_fp.sum()),
            "healthy_negative": int((~sick & ~positive).sum()),
        },
    }


def _downsample(values: np.ndarray, points: int = 200):
    n = len(values)
    if n <= points:
        return list(enumerate(values, start=1))
    idx = np.linspace(0, n - 1, points, dtype=int)
    return [(int(i) + 1, float(values[i])) for i in idx]
