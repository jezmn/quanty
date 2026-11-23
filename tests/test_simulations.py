import math

import pytest

from backend.simulations import bayes, birthday, clt, gambler, monty_hall


class TestBirthday:
    def test_bordes(self):
        assert birthday.theoretical_at_least_two_shared(1) == 0.0
        assert birthday.theoretical_at_least_two_shared(365) == pytest.approx(1.0)

    def test_n2_formula_cerrada(self):
        assert birthday.theoretical_at_least_two_shared(2) == pytest.approx(1 / 365), "n=2: P = 1 - 364/365"

    def test_n23_pasa_50(self):
        assert birthday.theoretical_at_least_two_shared(23) > 0.5, "23 people crosses 50%"

    def test_n30_valor_conocido(self):
        assert birthday.theoretical_at_least_two_shared(30) == pytest.approx(0.7063, abs=1e-3)

    def test_n60_valor_conocido(self):
        assert birthday.theoretical_at_least_two_shared(60) == pytest.approx(0.9941, abs=1e-3), "n=60 is nearly certain"

    def test_simulacion_converge(self):
        r = birthday.simulate(30, trials=4000, seed=42)
        assert r["simulated"] == pytest.approx(r["theoretical"], abs=0.03)


class TestMontyHall:
    def test_valores_teoricos(self):
        t = monty_hall.simulate(10_000, seed=1)["theoretical"]
        assert t["stay"] == pytest.approx(1 / 3)
        assert t["switch"] == pytest.approx(2 / 3)
        assert t["stay"] + t["switch"] == pytest.approx(1.0)

    def test_simulacion_converge(self):
        r = monty_hall.simulate(10_000, seed=7)
        assert r["simulated"]["stay"] == pytest.approx(1 / 3, abs=0.03)
        assert r["simulated"]["switch"] == pytest.approx(2 / 3, abs=0.03)


class TestBayes:
    def test_caso_clasico(self):
        r = bayes.simulate(0.01, 0.99, 0.01, population=200_000, seed=3)
        assert r["theoretical"] == pytest.approx(0.5, abs=0.01), "1% prevalence with 99/99 gives ~0.5"
        assert r["simulated"] == pytest.approx(0.5, abs=0.02)

    def test_conteos_de_poblacion_suman(self):
        r = bayes.simulate(0.01, 0.99, 0.01, population=50_000, seed=5)
        pop = r["population"]
        total = sum(pop.values())
        assert total == 50_000, f"population cells sum to {total}"


class TestGambler:
    def test_independencia(self):
        r = gambler.simulate(3000, seed=11)
        assert r["theoretical"] == 0.5, "a 5-head streak does not change the next flip"
        assert r["simulated"] == pytest.approx(0.5, abs=0.05)
        assert r["streaks_found"] >= 3000


class TestCLT:
    def test_parametros_poblacion(self):
        mu, sigma = clt.population_stats("uniform")
        assert mu == 5.0
        assert sigma == pytest.approx(10 / math.sqrt(12))
        assert clt.population_stats("bimodal") == (5.0, 5.0)

    def test_media_empirica_coincide(self):
        r = clt.simulate("exponential", sample_size=30, samples=10_000, seed=2)
        assert r["empirical"]["mean"] == pytest.approx(1.0, abs=0.02)
        assert r["empirical"]["std"] == pytest.approx(1 / math.sqrt(30), rel=0.1)

    def test_distribucion_invalida(self):
        with pytest.raises(KeyError):
            clt.simulate("triangular", 5, 100)
