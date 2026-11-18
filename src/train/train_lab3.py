from pathlib import Path
import os, time, hashlib, subprocess
import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "churn_v2.csv"
OUT = ROOT / "artifacts"
EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT_NAME", "AI381-Lab3-Churn")
TRACKING = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")

def git_commit():
    value = os.getenv("GITHUB_SHA") or os.getenv("COMMIT_SHA")
    if value:
        return value
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "local"



def main():
    df = pd.read_csv(DATA)
    fee_col = "monthly_fee" if "monthly_fee" in df.columns else "monthly_charges"
    numeric = ["tenure_months", fee_col, "support_calls"]
    categorical = ["contract", "internet_service"]
    X = df[numeric + categorical]
    y = df["churn"].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    tenure_test = X_test["tenure_months"].reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)
    mlflow.set_tracking_uri(TRACKING)
    mlflow.set_experiment(EXPERIMENT)
    data_hash = hashlib.sha256(DATA.read_bytes()).hexdigest()
    commit_sha = git_commit()

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=160, max_depth=8, random_state=42, class_weight="balanced"),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=100, max_depth=2, random_state=42),
    }
    OUT.mkdir(exist_ok=True)
    for name, estimator in candidates.items():
        pre = ColumnTransformer([
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ])
        model = Pipeline([("prep", pre), ("clf", estimator)])
        with mlflow.start_run(run_name=name) as run:
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            f1 = float(f1_score(y_test, pred, zero_division=0))
            auc = float(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
            new_mask = tenure_test <= 12
            established_mask = tenure_test > 12
            f1_new = float(f1_score(y_test[new_mask], pred[new_mask], zero_division=0)) if new_mask.any() else 0.0
            f1_established = float(f1_score(y_test[established_mask], pred[established_mask], zero_division=0)) if established_mask.any() else 0.0
            sample = X_test.iloc[[0]]
            timings=[]
            for _ in range(120):
                start=time.perf_counter(); model.predict_proba(sample); timings.append((time.perf_counter()-start)*1000)
            p95=float(np.percentile(timings,95))
            candidate_path=OUT/f"{name}.joblib"
            joblib.dump(model,candidate_path)
            size_mb=candidate_path.stat().st_size/(1024*1024)
            mlflow.log_params({"candidate":name,"random_state":42,"test_size":0.2,"data_file":DATA.name})
            mlflow.set_tags({"commit_sha": commit_sha, "data_sha256": data_hash, "dataset": DATA.name})
            mlflow.log_metrics({"f1":f1,"roc_auc":auc,"f1_tenure_le_12":f1_new,"f1_tenure_gt_12":f1_established,"p95_latency_ms":p95,"model_size_mb":size_mb})
            from mlflow.models import infer_signature
            signature = infer_signature(X_test, model.predict(X_test))
            mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name="AI381ChurnModel", signature=signature, input_example=sample)
            print(f"{name}: F1={f1:.3f}, AUC={auc:.3f}, slice(<=12m)={f1_new:.3f}, slice(>12m)={f1_established:.3f}, p95={p95:.3f}ms, size={size_mb:.3f}MB, run={run.info.run_id}")
    print("Training complete. Run: python src/train/promote_lab3.py")

if __name__ == "__main__":
    main()
