"""FastAPI service for the AI381 churn prediction model."""

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

MODEL_PATH = "model.joblib"

FEATURES = [
    "tenure_months",
    "monthly_fee",
    "support_calls",
    "contract",
    "internet_service",
]

app = FastAPI(title="AI381 Lab 1 churn API")

model = joblib.load(MODEL_PATH)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(customer: dict):
    # Check for missing input fields before using the model.
    missing = [feature for feature in FEATURES if feature not in customer]

    if missing:
        raise HTTPException(
            status_code=422,
            detail={"missing_fields": missing},
        )

    # Arrange the input columns in the model's expected order.
    X = pd.DataFrame([customer])[FEATURES]

    probability = float(model.predict_proba(X)[0, 1])

    return {"churn_probability": round(probability, 3)}