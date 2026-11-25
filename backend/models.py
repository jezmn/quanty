from pydantic import BaseModel, Field


class SeedInput(BaseModel):
    seed: int | None = Field(None, description="Optional seed for reproducibility")


class TrialsInput(SeedInput):
    trials: int = Field(10_000, ge=100, le=200_000)


class BirthdayInput(SeedInput):
    people: int = Field(30, ge=1, le=100)
    trials: int = Field(10_000, ge=100, le=100_000)


class BayesInput(SeedInput):
    prevalence: float = Field(0.01, gt=0, le=0.5)
    sensitivity: float = Field(0.99, ge=0.5, le=1.0)
    false_positive_rate: float = Field(0.01, gt=0, le=0.5)
    population: int = Field(10_000, ge=1_000, le=200_000)


class GamblerInput(SeedInput):
    streaks: int = Field(500, ge=10, le=5_000)


class CLTInput(SeedInput):
    distribution: str = "uniform"
    sample_size: int = Field(5, ge=1, le=500)
    samples: int = Field(20_000, ge=100, le=100_000)


class FrequenciesInput(BaseModel):
    values: list[float] = Field(..., min_length=5, max_length=10_000)


class RegressionInput(BaseModel):
    x: list[float] = Field(..., min_length=4, max_length=5_000)
    y: list[float] = Field(..., min_length=4, max_length=5_000)
    x0: float | None = Field(None, description="Optional x value to predict")
    x0: float | None = Field(None, ge=-1_000_000, le=1_000_000,
                             description="point to predict at")


class ConfidenceInput(SeedInput):
    hits: int = Field(300, ge=1)
    total: int = Field(400, ge=10, le=50_000)
    confidence: float = Field(0.99)
