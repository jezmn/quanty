import re
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_health_payload():
    r = client.get("/api/health")
    assert r.status_code == 200, f"health returned {r.status_code}"
    assert r.json() == {"status": "ok"}, f"unexpected payload: {r.json()}"


def test_unknown_api_path_is_404():
    r = client.get("/api/does-not-exist")
    assert r.status_code == 404, f"unknown API path returned {r.status_code}"


def test_unknown_static_path_is_404():
    r = client.get("/no-such-asset.css")
    assert r.status_code == 404, f"missing asset returned {r.status_code}"


def test_locale_sections_match():
    es = (ROOT / "frontend/js/locales/es.js").read_text()
    en = (ROOT / "frontend/js/locales/en.js").read_text()
    es_keys = set(re.findall(r"^  (\w+):", es, re.M))
    en_keys = set(re.findall(r"^  (\w+):", en, re.M))
    assert es_keys == en_keys, f"only ES: {sorted(es_keys - en_keys)}, only EN: {sorted(en_keys - es_keys)}"


def test_readme_documents_venv_activation():
    readme = (ROOT / "README.md").read_text()
    assert "source .venv/bin/activate" in readme, "Quick start must show how to activate the venv"
