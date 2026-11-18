from pathlib import Path
import json
import os

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / "artifacts"
CHAMPION_PATH = ARTIFACT_DIR / "champion.joblib"
MODEL_PATH = ROOT / "model.joblib"
ACTIVE_MODEL_PATH = CHAMPION_PATH if CHAMPION_PATH.exists() else MODEL_PATH
METADATA_PATH = ARTIFACT_DIR / "champion_metadata.json"
FEATURES = ["tenure_months", "monthly_fee", "support_calls", "contract", "internet_service"]

app = FastAPI(title="AI381 Lab 3 Churn Prediction API", version="3.0.0")
model = joblib.load(ACTIVE_MODEL_PATH)
metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8")) if METADATA_PATH.exists() else {}


class CustomerInput(BaseModel):
    tenure_months: float = Field(ge=0)
    monthly_fee: float = Field(ge=0)
    support_calls: int = Field(ge=0)
    contract: str
    internet_service: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_file": ACTIVE_MODEL_PATH.name,
        "model_version": metadata.get("model_version", "local-unregistered"),
        "mlflow_run_id": metadata.get("mlflow_run_id", "unknown"),
        "commit_sha": metadata.get("commit_sha", os.getenv("COMMIT_SHA", "unknown")),
        "image_tag": metadata.get("image_tag", os.getenv("IMAGE_TAG", "local")),
    }


@app.post("/predict")
def predict(customer: CustomerInput):
    X = pd.DataFrame([customer.model_dump()])[FEATURES]
    probability = float(model.predict_proba(X)[0, 1])
    return {"churn_probability": round(probability, 3)}
