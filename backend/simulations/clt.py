import numpy as np


DISTRIBUTIONS = {
    "uniform": {
        "label": "Uniforme [0, 10)",
        "sample": lambda rng, size, n: rng.uniform(0, 10, size=(size, n)),
    },
    "exponential": {
        "label": "Exponencial (lambda = 1)",
        "sample": lambda rng, size, n: rng.exponential(1.0, size=(size, n)),
    },
    "bimodal": {
        "label": "Bimodal (0/10 con 50% cada una)",
        "sample": lambda rng, size, n: np.where(
            rng.random(size=(size, n)) < 0.5, 0.0, 10.0
        ),
    },
}


def population_stats(name: str) -> tuple[float, float]:
    if name == "uniform":
        return 5.0, 10.0 / np.sqrt(12)
    if name == "exponential":
        return 1.0, 1.0
    if name == "bimodal":
        return 5.0, 5.0
    raise KeyError(f"unknown distribution: {name}")


def simulate(
    distribution: str,
    sample_size: int,
    samples: int,
    seed: int | None = None,
) -> dict:
    dist = DISTRIBUTIONS[distribution]
    rng = np.random.default_rng(seed)

    draws = dist["sample"](rng, samples, sample_size)
    means = draws.mean(axis=1)

    mu, sigma = population_stats(distribution)
    se = sigma / np.sqrt(sample_size)

    hist, edges = np.histogram(means, bins=40, density=True)
    bin_centers = (edges[:-1] + edges[1:]) / 2

    normal_density = (
        1.0 / (se * np.sqrt(2 * np.pi)) * np.exp(-((bin_centers - mu) ** 2) / (2 * se**2))
    )

    return {
        "theoretical": {"mu": float(mu), "sigma": float(sigma), "se": float(se)},
        "empirical": {
            "mean": float(means.mean()),
            "std": float(means.std()),
        },
        "histogram": {
            "centers": bin_centers.tolist(),
            "density": hist.tolist(),
            "normal": normal_density.tolist(),
        },
    }
