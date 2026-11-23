import numpy as np


def _design(x: np.ndarray, degree: int) -> np.ndarray:
    return np.column_stack([x**j for j in range(degree + 1)])


def fit(x: list[float], y: list[float], degree: int) -> dict:
    xv = np.asarray(x, dtype=float)
    yv = np.asarray(y, dtype=float)
    n = xv.size
    if n < degree + 2:
        raise ValueError(f"degree {degree} requires at least {degree + 2} points")

    X = _design(xv, degree)
    p = degree + 1
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)

    fitted = X @ beta
    residuals = yv - fitted
    sse = float((residuals**2).sum())
    sst = float(((yv - yv.mean()) ** 2).sum())
    r2 = 1 - sse / sst if sst > 0 else 0.0
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - p)
    se = float(np.sqrt(sse / (n - p)))

    return {
        "degree": degree,
        "coefficients": [float(b) for b in beta],
        "r2": float(r2),
        "r2_adjusted": float(r2_adj),
        "se": se,
        "press": float(press(X, residuals)),
        "residuals": [float(e) for e in residuals],
        "fitted": [float(v) for v in fitted],
    }


def press(X: np.ndarray, residuals: np.ndarray) -> float:
    hat = X @ np.linalg.pinv(X.T @ X) @ X.T
    h = np.clip(np.diag(hat), 0.0, 1.0 - 1e-12)
    return float(((residuals / (1 - h)) ** 2).sum())


def predict(model: dict, x0: float) -> float:
    return float(sum(c * x0**j for j, c in enumerate(model["coefficients"])))


def simulate(x: list[float], y: list[float]) -> dict:
    linear = fit(x, y, degree=1)
    quadratic = fit(x, y, degree=2)
    best = "quadratic" if quadratic["press"] < linear["press"] else "linear"
    xs = np.linspace(min(x), max(x), 100)
    return {
        "models": {"linear": linear, "quadratic": quadratic},
        "best": best,
        "n": len(x),
        "scatter": {"x": [float(v) for v in x], "y": [float(v) for v in y]},
        "curves": {
            "linear": {"x": xs.tolist(), "y": [_eval(linear["coefficients"], v) for v in xs]},
            "quadratic": {"x": xs.tolist(), "y": [_eval(quadratic["coefficients"], v) for v in xs]},
        },
    }


def predict_note(x: list[float], y: list[float], x0: float) -> dict:
    linear = fit(x, y, degree=1)
    quadratic = fit(x, y, degree=2)
    return {"x0": x0, "linear": predict(linear, x0), "quadratic": predict(quadratic, x0)}


def _eval(coef: list[float], x: float) -> float:
    return sum(c * x**j for j, c in enumerate(coef))
