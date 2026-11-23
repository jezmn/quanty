from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestFrontend:
    def test_index_renderiza_todas_las_rondas(self):
        html = client.get("/").text
        assert "@ROUNDS@" not in html, "renderer must replace the marker"
        for tab_id in ("birthday", "monty", "bayes", "gambler",
                       "clt", "frequencies", "regression", "confidence", "score"):
            assert tab_id in html
        assert 'active === \'score\'' in html
        for key in ("r6.num", "r7.num", "r8.num"):
            assert f"i18n.t('{key}')" in html, f"section {key} was not injected"

    def test_assets_estaticos(self):
        css = client.get("/css/styles.css")
        js = client.get("/js/app.js")
        assert css.status_code == 200
        assert js.status_code == 200

    def test_path_traversal_bloqueado(self):
        assert client.get("/../../etc/passwd").status_code in (400, 404)


class TestEndpointsNuevos:
    def test_frequencies_ok(self):
        r = client.post("/api/frequencies", json={"values": [1, 2, 3, 4, 5, 6, 7, 8]})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["summary"]["n"] == 8, "all 8 values must be counted"
        assert len(body["table"]) == body["summary"]["classes"]

    def test_frequencies_datos_invalidos(self):
        assert client.post("/api/frequencies", json={"values": [1, 2]}).status_code == 422

    def test_regression_ok_con_prediccion(self):
        payload = {"x": [0, 1, 2, 3, 4], "y": [1, 4, 9, 16, 25], "x0": 10}
        r = client.post("/api/regression", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["best"] in ("linear", "quadratic")
        assert abs(body["prediction"]["quadratic"] - 121) < 1e-6, "quadratic fit at x0=10 is 121"

    def test_regression_datos_invalidos(self):
        r = client.post("/api/regression", json={"x": [1, 2, 3], "y": [1, 2]})
        assert r.status_code == 422

    def test_confidence_caso_lab5(self):
        r = client.post("/api/confidence", json={"hits": 300, "total": 400, "confidence": 0.99})
        assert r.status_code == 200
        ic = r.json()["interval"]
        assert ic["lower"] < 0.75 < ic["upper"], f"interval must contain p-hat: {ic}"

    def test_confidence_validaciones(self):
        assert client.post("/api/confidence", json={"hits": 11, "total": 10}).status_code == 400
        bad = {"hits": 5, "total": 10, "confidence": 0.80}
        assert client.post("/api/confidence", json=bad).status_code == 400

    def test_rate_limit(self):
        from backend.main import app

        mw = app.middleware_stack
        rl = None
        node = mw
        while node is not None:
            rl = getattr(node, "app", None)
            if rl is not None and hasattr(rl, "hits"):
                break
            node = rl
        assert rl is not None, "rate limit middleware not found"
        rl.hits.clear()
        for _ in range(3):
            assert client.get("/api/health").status_code == 200
        rl.hits["testclient"].extend([0.0] * 60)
        assert client.get("/api/health").status_code == 429
        rl.hits.clear()

    def test_health(self):
        assert client.get("/api/health").json() == {"status": "ok"}, "health payload changed"
