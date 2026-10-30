from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "model.joblib"

FEATURES = [
    "tenure_months",
    "monthly_fee",
    "support_calls",
    "contract",
    "internet_service",
]

app = FastAPI(title="AI381 Churn Prediction API")

model = joblib.load(MODEL_PATH)


class CustomerInput(BaseModel):
    tenure_months: float = Field(ge=0)
    monthly_fee: float = Field(ge=0)
    support_calls: int = Field(ge=0)
    contract: str
    internet_service: str


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
def predict(customer: CustomerInput):
    customer_data = customer.dict()

    X = pd.DataFrame([customer_data])[FEATURES]

    probability = float(model.predict_proba(X)[0, 1])

    return {
        "churn_probability": round(probability, 3)
    }