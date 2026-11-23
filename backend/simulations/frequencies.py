import math

import numpy as np


def build_table(values: list[float]) -> dict:
    data = np.asarray(values, dtype=float)
    n = data.size
    if n < 5:
        raise ValueError("at least 5 values are required")

    lo, hi = float(data.min()), float(data.max())
    k = max(5, round(1 + 3.322 * math.log10(n)))
    amplitude = max((hi - lo) / k, 1e-12)

    freq, edges = np.histogram(data, bins=k, range=(lo, hi))
    centers = (edges[:-1] + edges[1:]) / 2
    cum = np.cumsum(freq)

    rows = [
        {
            "lower": float(edges[i]),
            "upper": float(edges[i + 1]),
            "center": float(centers[i]),
            "frequency": int(freq[i]),
            "cumulative": int(cum[i]),
            "relative": float(freq[i] / n),
            "percent": float(freq[i] / n * 100),
        }
        for i in range(k)
    ]

    return {
        "summary": {
            "n": n,
            "min": lo,
            "max": hi,
            "range": hi - lo,
            "classes": k,
            "amplitude": amplitude,
        },
        "table": rows,
        **grouped_stats(rows, n),
        "raw": {
            "mean": float(data.mean()),
            "median": float(np.median(data)),
            "quartiles": [float(q) for q in np.percentile(data, [25, 50, 75])],
        },
        "histogram": {
            "labels": [f"{r['lower']:.2f}-{r['upper']:.2f}" for r in rows],
            "frequency": [r["frequency"] for r in rows],
        },
    }


def grouped_stats(rows: list[dict], n: int) -> dict:
    centers = np.array([r["center"] for r in rows])
    freq = np.array([r["frequency"] for r in rows], dtype=float)
    cum_prev = np.concatenate(([0.0], np.cumsum(freq)[:-1]))

    return {
        "mean": float((centers * freq).sum() / n),
        "median": _positional(0.5, rows, freq, cum_prev, n),
        "mode": _mode(rows, freq),
        "q1": _positional(0.25, rows, freq, cum_prev, n),
        "q3": _positional(0.75, rows, freq, cum_prev, n),
    }


def _class_index(pos: float, freq, n: int) -> int:
    target = pos * n
    return int(np.searchsorted(np.cumsum(freq), target, side="right"))


def _positional(q: float, rows, freq, cum_prev, n: int) -> float:
    i = _class_index(q, freq, n)
    row = rows[i]
    F, f = cum_prev[i], freq[i]
    if f == 0:
        return row["center"]
    width = row["upper"] - row["lower"]
    return row["lower"] + width * ((q * n - F) / f)


def _mode(rows, freq) -> float:
    i = int(np.argmax(freq))
    row = rows[i]
    d1 = freq[i] - (freq[i - 1] if i > 0 else 0)
    d2 = freq[i] - (freq[i + 1] if i < len(freq) - 1 else 0)
    if d1 + d2 == 0:
        return row["center"]
    width = row["upper"] - row["lower"]
    return row["lower"] + width * d1 / (d1 + d2)
