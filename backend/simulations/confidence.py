import numpy as np

Z = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}


def interval(hits: int, total: int, confidence: float = 0.95) -> dict:
    if total <= 0:
        raise ValueError("total must be positive")
    if confidence not in Z:
        raise ValueError(f"confianza soportada: {sorted(Z)}")

    p_hat = hits / total
    z = Z[confidence]
    se = float(np.sqrt(p_hat * (1 - p_hat) / total))
    half = z * se
    return {
        "p_hat": p_hat,
        "se": se,
        "margin": float(half),
        "lower": float(max(0.0, p_hat - half)),
        "upper": float(min(1.0, p_hat + half)),
        "z": z,
        "confidence": confidence,
    }


def coverage_simulation(true_p: float, n: int, confidence: float,
                        replicates: int = 2000, seed: int | None = None) -> dict:
    rng = np.random.default_rng(seed)
    in_interval = 0
    bounds: list[tuple[float, float]] = []

    for _ in range(replicates):
        hits = int(rng.binomial(n, true_p))
        ic = interval(hits, n, confidence)
        if ic["lower"] <= true_p <= ic["upper"]:
            in_interval += 1
        bounds.append((ic["lower"], ic["upper"]))

    lows, highs = np.array(bounds).T
    return {
        "true_p": true_p,
        "n": n,
        "confidence": confidence,
        "replicates": replicates,
        "coverage": in_interval / replicates,
        "intervals_sample": [
            {"lower": float(l), "upper": float(h)}
            for l, h in bounds[:100]
        ],
        "mean_width": float((highs - lows).mean()),
    }


def simulate(hits: int, total: int, confidence: float,
             true_p: float | None = None, seed: int | None = None) -> dict:
    p = true_p if true_p is not None else hits / total
    return {
        "interval": interval(hits, total, confidence),
        "coverage": coverage_simulation(p, total, confidence, seed=seed),
    }
