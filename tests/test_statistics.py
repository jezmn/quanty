import math

import numpy as np
import pytest

from backend.simulations import confidence, frequencies, regression

SATISFACTION = [75, 37, 89, 95, 67, 60, 55, 43, 32, 39, 40, 58, 69, 74, 80,
                96, 92, 40, 35, 39, 51, 73, 70, 77, 86, 84, 80, 75, 77, 42,
                49, 52, 68, 64, 60, 76, 74, 73, 71, 87, 98, 91, 46, 62, 60,
                42, 50, 76, 70, 64]

BATTERY_X = [0.0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
BATTERY_Y = [9.1, 7.3, 3.2, 4.6, 4.8, 2.9, 5.7, 7.1, 8.8, 10.2]


class TestFrequencies:
    def test_summary_sturges(self):
        r = frequencies.build_table(SATISFACTION)
        s = r["summary"]
        n, lo, hi = s["n"], s["min"], s["max"]
        k_esperado = round(1 + 3.322 * math.log10(50))
        assert s["classes"] == k_esperado, f"Sturges expects {k_esperado}"
        assert abs(s["amplitude"] - (hi - lo) / k_esperado) < 1e-9

    def test_frecuencias_suman_n(self):
        r = frequencies.build_table(SATISFACTION)
        assert sum(row["frequency"] for row in r["table"]) == 50
        assert sum(row["relative"] for row in r["table"]) == pytest.approx(1.0)
        acc = [row["cumulative"] for row in r["table"]]
        assert acc == sorted(acc) and acc[-1] == 50, "cumulative must be monotonic and end at n"

    def test_estadisticos_agrupados_cerca_de_reales(self):
        r = frequencies.build_table(SATISFACTION)
        assert r["mean"] == pytest.approx(float(np.mean(SATISFACTION)), abs=1.5)
        assert r["median"] == pytest.approx(float(np.median(SATISFACTION)), abs=4.0)
        assert r["q1"] <= r["median"] <= r["q3"] <= r["summary"]["max"]

    def test_datos_constantes_no_dividen_por_cero(self):
        r = frequencies.build_table([5.0] * 20)
        assert r["mean"] == pytest.approx(5.0)

    def test_pocos_datos_rechazados(self):
        with pytest.raises(ValueError):
            frequencies.build_table([1, 2, 3])


class TestRegression:
    def test_lineal_exacta(self):
        r = regression.fit([0, 1, 2, 3, 4], [1, 3, 5, 7, 9], degree=1)
        assert r["r2"] == pytest.approx(1.0, abs=1e-9), "exact linear fit has R2 = 1"
        assert r["coefficients"][0] == pytest.approx(1.0)
        assert r["coefficients"][1] == pytest.approx(2.0)
        assert r["se"] < 1e-9

    def test_criterios_en_rango(self):
        r = regression.fit(BATTERY_X, BATTERY_Y, degree=2)
        assert 0 <= r["r2"] <= 1
        assert r["r2_adjusted"] <= r["r2"] + 1e-12
        assert r["press"] >= sum(e**2 for e in r["residuals"]) - 1e-6, "PRESS must be at least SSE"

    def test_mejor_modelo_por_press(self):
        r = regression.simulate(BATTERY_X, BATTERY_Y)
        esperado = min(r["models"], key=lambda k: r["models"][k]["press"])
        assert r["best"] == esperado

    def test_prediccion_cuadratica_conocida(self):
        r = regression.fit([0, 1, 2, 3, 4], [1, 4, 9, 16, 25], degree=2)
        assert regression.predict(r, 10) == pytest.approx(121.0, abs=1e-6), "(x+1)^2 at x=10 is 121"

    def test_puntos_insuficientes(self):
        with pytest.raises(ValueError):
            regression.fit([0, 1], [1, 2], degree=2)


class TestConfidence:
    def test_caso_del_lab5_300_de_400(self):
        ic = confidence.interval(300, 400, 0.99)
        assert ic["p_hat"] == pytest.approx(0.75)
        assert ic["se"] == pytest.approx(math.sqrt(0.75 * 0.25 / 400))
        assert ic["lower"] == pytest.approx(0.6942, abs=1e-3), "lab interval lower bound"
        assert ic["upper"] == pytest.approx(0.8058, abs=1e-3)

    def test_intervalo_contiene_a_p_hat(self):
        ic = confidence.interval(150, 400, 0.95)
        assert ic["lower"] < ic["p_hat"] < ic["upper"]

    def test_cobertura_converge_al_nivel(self):
        r = confidence.coverage_simulation(0.75, 100, 0.95,
                                           replicates=3000, seed=7)
        assert r["coverage"] == pytest.approx(0.95, abs=0.02)

    def test_confianza_no_soportada(self):
        with pytest.raises(ValueError):
            confidence.interval(1, 10, 0.80)

    def test_total_invalido(self):
        with pytest.raises(ValueError):
            confidence.interval(0, 0, 0.95)
