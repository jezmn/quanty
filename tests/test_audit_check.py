import math
from fastapi.testclient import TestClient

from backend.main import app

TOL = 1e-9


def approx(a, b, tol=1e-4):
    assert abs(a - b) < tol, f"{a} vs {b}"


def test_birthday_exact_progression():
    c = TestClient(app)
    for n in (2, 10, 23, 30, 50):
        p = 1 - math.prod((365 - i) / 365 for i in range(n))
        r = c.post("/api/birthday", json={"people": n, "trials": 30000}).json()
        approx(r["theoretical"], p, TOL)
        assert abs(r["simulated"] - p) < 0.02
    r2 = c.post("/api/birthday", json={"people": 2, "trials": 5000}).json()
    approx(r2["theoretical"], 1 / 365, TOL)
    r23 = c.post("/api/birthday", json={"people": 23, "trials": 100}).json()
    assert r23["theoretical"] > 0.5
    r60 = c.post("/api/birthday", json={"people": 60, "trials": 100}).json()
    approx(r60["theoretical"], 1 - math.prod((365 - i) / 365 for i in range(60)), TOL)


def test_monty_hall_honest_frequencies():
    c = TestClient(app)
    r = c.post("/api/monty-hall", json={"trials": 60000}).json()
    approx(r["theoretical"]["stay"], 1 / 3, TOL)
    approx(r["theoretical"]["switch"], 2 / 3, TOL)
    assert abs(r["simulated"]["stay"] - 1 / 3) < 0.01
    assert abs(r["simulated"]["switch"] - 2 / 3) < 0.01
    assert abs(r["simulated"]["stay"] + r["simulated"]["switch"] - 1) < TOL


def test_bayes_classic_case_is_exactly_one_half():
    c = TestClient(app)
    r = c.post("/api/bayes", json={
        "prevalence": 0.01, "sensitivity": 0.99,
        "false_positive_rate": 0.01, "population": 50000,
    }).json()
    approx(r["theoretical"], 0.5, TOL)
    assert abs(r["simulated"] - 0.5) < 0.05
    pop = r["population"]
    approx(sum(pop.values()), 50000, TOL)
    prev, sens, fpr = 0.04, 0.9, 0.2
    expect = sens * prev / (sens * prev + fpr * (1 - prev))
    r2 = c.post("/api/bayes", json={
        "prevalence": prev, "sensitivity": sens,
        "false_positive_rate": fpr, "population": 10000,
    }).json()
    approx(r2["theoretical"], expect, TOL)
    assert abs(r2["simulated"] - expect) < 0.05


def test_gambler_still_a_fair_coin():
    c = TestClient(app)
    r = c.post("/api/gambler", json={"streaks": 3000}).json()
    approx(r["theoretical"], 0.5, TOL)
    assert abs(r["simulated"] - 0.5) < 0.05
    assert r["streaks_found"] >= 3000
    assert len(r["convergence"]) == r["streaks_found"]


def test_clt_theory_and_empirical_match():
    c = TestClient(app)
    cases = {
        "uniform": (5.0, 10.0 / math.sqrt(12)),
        "exponential": (1.0, 1.0),
        "bimodal": (5.0, 5.0),
    }
    for dist, (mu, sigma) in cases.items():
        for n in (1, 5, 40):
            r = c.post("/api/clt", json={
                "distribution": dist, "sample_size": n, "samples": 40000,
            }).json()
            approx(r["theoretical"]["mu"], mu, TOL)
            approx(r["theoretical"]["sigma"], sigma, TOL)
            approx(r["theoretical"]["se"], sigma / math.sqrt(n), TOL)
            assert abs(r["empirical"]["mean"] - mu) < 0.15 * max(1, sigma / math.sqrt(n))
            assert abs(r["empirical"]["std"] - sigma / math.sqrt(n)) < 0.1 * max(1e-9, sigma / math.sqrt(n)) + 0.05


def test_frequencies_table_is_self_consistent():
    c = TestClient(app)
    values = [2, 3, 3, 4, 4, 5, 5, 5, 6, 7, 8, 9, 10, 10, 12, 15, 18, 20, 22, 25]
    r = c.post("/api/frequencies", json={"values": values}).json()
    assert r["summary"]["n"] == len(values)
    k_expect = max(5, round(1 + 3.322 * math.log10(len(values))))
    assert r["summary"]["classes"] == k_expect
    table = r["table"]
    assert all(row["frequency"] == 0 or row["frequency"] >= 1 for row in table)
    assert sum(row["frequency"] for row in table) == len(values)
    cums = [row["cumulative"] for row in table]
    assert cums[-1] == len(values) and all(cums[i] <= cums[i + 1] for i in range(len(cums) - 1))
    assert abs(sum(row["relative"] for row in table) - 1) < 1e-9
    mean_expect = sum(row["frequency"] * row["center"] for row in table) / len(values)
    approx(r["mean"], mean_expect, TOL)
    n, half = len(values), len(values) / 2
    med = None
    for i, row in enumerate(table):
        f = row["frequency"]
        if cums[i] >= half and f > 0:
            F_prev = cums[i - 1] if i else 0
            width = row["upper"] - row["lower"]
            med = row["lower"] + (half - F_prev) / f * width
            break
    approx(r["median"], med, 1e-6)


def test_regression_vs_polyfit_and_bruteforce_press():
    import numpy as np
    c = TestClient(app)
    x = [0.0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    y = [9.1, 7.3, 3.2, 4.6, 4.8, 2.9, 5.7, 7.1, 8.8, 10.2]
    r = c.post("/api/regression", json={"x": x, "y": y, "x0": 5.5}).json()
    xv, yv = np.array(x), np.array(y)

    for key, deg in (("linear", 1), ("quadratic", 2)):
        m = r["models"][key]
        coefs = np.polyfit(xv, yv, deg)[::-1]
        assert np.allclose(m["coefficients"], coefs, atol=1e-6)
        pred = np.polyval(coefs[::-1], xv)
        sse = float(((yv - pred) ** 2).sum())
        sst = float(((yv - yv.mean()) ** 2).sum())
        approx(m["r2"], 1 - sse / sst, 1e-6)

    def loo_press(deg):
        total = 0.0
        for i in range(len(x)):
            xs = xv[np.arange(len(x)) != i]
            ys = yv[np.arange(len(y)) != i]
            c_i = np.polyfit(xs, ys, deg)
            total += (yv[i] - np.polyval(c_i, xv[i])) ** 2
        return total

    lin, quad = r["models"]["linear"], r["models"]["quadratic"]
    approx(lin["press"], loo_press(1), 1e-2)
    approx(quad["press"], loo_press(2), 1e-2)
    best = "quadratic" if quad["press"] < lin["press"] else "linear"
    assert r["best"] == best
    p1 = np.polyval(r["models"]["linear"]["coefficients"][::-1], 5.5)
    approx(r["prediction"]["linear"], float(p1), 1e-6)


def test_confidence_explicit_case_and_coverage():
    c = TestClient(app)
    r = c.post("/api/confidence", json={"hits": 300, "total": 400, "confidence": 0.99}).json()
    ic = r["interval"]
    p_hat, z, n = 0.75, 2.576, 400
    se_expect = math.sqrt(p_hat * (1 - p_hat) / n)
    approx(ic["se"], se_expect, TOL)
    approx(ic["lower"], p_hat - z * se_expect, TOL)
    approx(ic["upper"], p_hat + z * se_expect, TOL)
    approx(ic["lower"], 0.6942, 1e-3)
    approx(ic["upper"], 0.8058, 1e-3)
    cov = r["coverage"]
    assert abs(cov["coverage"] - 0.99) < 0.02
    assert cov["replicates"] == 2000 and len(cov["intervals_sample"]) == 100
    r95 = c.post("/api/confidence", json={"hits": 300, "total": 400, "confidence": 0.95}).json()
    assert r95["interval"]["margin"] < ic["margin"]
