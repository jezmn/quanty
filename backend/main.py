from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from backend import models
from backend.ratelimit import RateLimitMiddleware
from backend.renderer import FRONTEND, render_index
from backend.simulations import (
    bayes,
    birthday,
    clt,
    confidence,
    frequencies,
    gambler,
    monty_hall,
    regression,
)

app = FastAPI(title="Quanty API", version="1.0.0")
app.add_middleware(RateLimitMiddleware)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/")
def serve_index():
    return HTMLResponse(render_index())


@app.post("/api/birthday")
def birthday_endpoint(data: models.BirthdayInput):
    max_curve = min(max(data.people, 0) + 5, 80)
    return {
        "theoretical_curve": birthday.theoretical_curve(max_curve),
        **birthday.simulate(data.people, data.trials, seed=data.seed),
    }


@app.post("/api/monty-hall")
def monty_hall_endpoint(data: models.TrialsInput):
    return monty_hall.simulate(data.trials, seed=data.seed)


@app.post("/api/bayes")
def bayes_endpoint(data: models.BayesInput):
    return bayes.simulate(
        data.prevalence,
        data.sensitivity,
        data.false_positive_rate,
        data.population,
        seed=data.seed,
    )


@app.post("/api/gambler")
def gambler_endpoint(data: models.GamblerInput):
    return gambler.simulate(data.streaks, seed=data.seed)


@app.post("/api/clt")
def clt_endpoint(data: models.CLTInput):
    if data.distribution not in clt.DISTRIBUTIONS:
        raise HTTPException(400, "Unsupported distribution")
    return clt.simulate(
        data.distribution, data.sample_size, data.samples, seed=data.seed
    )


@app.post("/api/frequencies")
def frequencies_endpoint(data: models.FrequenciesInput):
    try:
        return frequencies.build_table(data.values)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.post("/api/regression")
def regression_endpoint(data: models.RegressionInput):
    if len(data.x) != len(data.y):
        raise HTTPException(400, "x and y must have the same length")
    try:
        result = regression.simulate(data.x, data.y)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    if data.x0 is not None:
        result["prediction"] = regression.predict_note(data.x, data.y, data.x0)
    return result


@app.post("/api/confidence")
def confidence_endpoint(data: models.ConfidenceInput):
    if data.confidence not in confidence.Z:
        raise HTTPException(400, f"supported confidence levels: {sorted(confidence.Z)}")
    if data.hits > data.total:
        raise HTTPException(400, "hits cannot exceed total")
    return confidence.simulate(
        data.hits,
        data.total,
        data.confidence,
        seed=data.seed,
    )


@app.get("/{path:path}")
def serve_frontend(path: str):
    if path.startswith("api/"):
        raise HTTPException(404, "Not found")
    file = (FRONTEND / (path or "index.html")).resolve()
    try:
        file.relative_to(FRONTEND.resolve())
    except ValueError:
        raise HTTPException(404, "Not found") from None
    if file.is_file():
        return FileResponse(file)
    raise HTTPException(404, "Not found")
