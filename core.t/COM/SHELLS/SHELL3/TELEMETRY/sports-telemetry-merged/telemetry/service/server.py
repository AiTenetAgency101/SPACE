from fastapi import FastAPI
from telemetry.math.implied_probability import implied_probability
from telemetry.math.momentum import momentum
from telemetry.math.variance import variance
from telemetry.math.entropy import entropy
from telemetry.math.drift import drift

app = FastAPI()

@app.get("/metrics")
def metrics():
    # placeholder example
    return {
        "prob": implied_probability(2.0),
        "momentum": momentum([0.2, 0.25]),
        "variance": variance([0.2, 0.25, 0.3]),
        "entropy": entropy([0.5, 0.5]),
        "drift": drift(0.3, 0.2)
    }
