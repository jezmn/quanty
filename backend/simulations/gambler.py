import numpy as np

STREAK = 5


def theoretical() -> float:
    return 0.5


def simulate(follows: int, seed: int | None = None) -> dict:
    rng = np.random.default_rng(seed)

    results_after: list[bool] = []
    streak = 0
    flips = 0
    max_flips = max(follows, 1) * 300

    while len(results_after) < follows and flips < max_flips:
        heads = rng.random() < 0.5
        flips += 1
        streak = streak + 1 if heads else 0
        if streak == STREAK:
            next_heads = rng.random() < 0.5
            results_after.append(next_heads)
            streak = 1 if next_heads else 0

    hits = np.cumsum(results_after)
    running = hits / np.arange(1, len(results_after) + 1)

    return {
        "theoretical": theoretical(),
        "simulated": float(running[-1]) if len(running) else None,
        "convergence": [
            {"trial": t, "estimate": float(e)}
            for t, e in enumerate(running, start=1)
        ],
        "streaks_found": len(results_after),
        "flips_used": flips,
    }
