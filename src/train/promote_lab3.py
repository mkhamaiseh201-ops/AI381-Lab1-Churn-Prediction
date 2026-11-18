from pathlib import Path
import json
import os
import subprocess

import joblib
import mlflow
from mlflow.tracking import MlflowClient

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)
TRACKING = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT_NAME", "AI381-Lab3-Churn")
MODEL_NAME = "AI381ChurnModel"
MIN_F1 = float(os.getenv("GATE_MIN_F1", "0.50"))
MIN_SLICE_F1 = float(os.getenv("GATE_MIN_SLICE_F1", "0.35"))
MAX_P95_MS = float(os.getenv("GATE_MAX_P95_MS", "1000"))
MAX_SIZE_MB = float(os.getenv("GATE_MAX_SIZE_MB", "50"))
MIN_F1_GAIN = float(os.getenv("GATE_MIN_F1_GAIN", "0.005"))
FORCE_BLOCK = os.getenv("GATE_FORCE_BLOCK", "false").lower() == "true"


def current_commit():
    value = os.getenv("GITHUB_SHA") or os.getenv("COMMIT_SHA")
    if value:
        return value
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "local"


def main():
    mlflow.set_tracking_uri(TRACKING)
    client = MlflowClient()
    exp = client.get_experiment_by_name(EXPERIMENT)
    if exp is None:
        raise SystemExit("Experiment not found. Run train_lab3.py first.")

    commit = current_commit()
    runs = client.search_runs(
        [exp.experiment_id],
        filter_string=f"tags.commit_sha = '{commit}'",
        order_by=["metrics.f1 DESC"],
        max_results=100,
    )
    if not runs:
        raise SystemExit(f"No candidate runs found for commit {commit}.")

    passed = []
    for run in runs:
        m = run.data.metrics
        checks = {
            "overall_f1": m.get("f1", 0) >= MIN_F1,
            "slice_tenure_le_12": m.get("f1_tenure_le_12", 0) >= MIN_SLICE_F1,
            "slice_tenure_gt_12": m.get("f1_tenure_gt_12", 0) >= MIN_SLICE_F1,
            "p95_latency": m.get("p95_latency_ms", float("inf")) <= MAX_P95_MS,
            "model_size": m.get("model_size_mb", float("inf")) <= MAX_SIZE_MB,
        }
        print(f"{run.data.params.get('candidate', run.info.run_id)}: {checks}")
        if all(checks.values()):
            passed.append(run)

    if FORCE_BLOCK or not passed:
        raise SystemExit("PROMOTION BLOCKED: candidate failed the configured promotion gate.")

    best = max(passed, key=lambda r: r.data.metrics["f1"])
    try:
        champion = client.get_model_version_by_alias(MODEL_NAME, "champion")
    except Exception:
        champion = None

    if champion is not None:
        champion_run = client.get_run(champion.run_id)
        champion_f1 = champion_run.data.metrics.get("f1")
        if champion_f1 is None:
            raise SystemExit("PROMOTION BLOCKED: current champion has no recorded F1 metric.")
        gain = best.data.metrics["f1"] - champion_f1
        print(f"Champion F1={champion_f1:.4f}; candidate F1={best.data.metrics['f1']:.4f}; gain={gain:.4f}; required={MIN_F1_GAIN:.4f}")
        if gain < MIN_F1_GAIN:
            raise SystemExit("PROMOTION BLOCKED: candidate does not improve enough over champion.")

    model = mlflow.sklearn.load_model(f"runs:/{best.info.run_id}/model")
    joblib.dump(model, OUT / "champion.joblib")
    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    matching = [v for v in versions if v.run_id == best.info.run_id]
    if not matching:
        raise SystemExit("Registered model version for selected run was not found.")
    version = max(matching, key=lambda v: int(v.version))
    client.set_registered_model_alias(MODEL_NAME, "champion", version.version)
    metadata = {
        "model_name": MODEL_NAME,
        "model_version": str(version.version),
        "mlflow_run_id": best.info.run_id,
        "commit_sha": commit,
        "image_tag": os.getenv("IMAGE_TAG", commit),
        "f1": best.data.metrics["f1"],
    }
    (OUT / "champion_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    for key, value in metadata.items():
        client.set_model_version_tag(MODEL_NAME, version.version, key, str(value))
    print(f"PROMOTED: {best.data.params.get('candidate')} | run={best.info.run_id} | version={version.version} | F1={best.data.metrics['f1']:.3f}")
    print(f"Saved serving model: {OUT / 'champion.joblib'}")


if __name__ == "__main__":
    main()
