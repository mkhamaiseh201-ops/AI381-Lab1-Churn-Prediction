from pathlib import Path
import os, joblib, mlflow
from mlflow.tracking import MlflowClient

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"artifacts"; OUT.mkdir(exist_ok=True)
TRACKING=os.getenv("MLFLOW_TRACKING_URI","http://127.0.0.1:5000")
EXPERIMENT=os.getenv("MLFLOW_EXPERIMENT_NAME","AI381-Lab3-Churn")
MODEL_NAME="AI381ChurnModel"
# Promotion gate: quality + operational limits. Adjust only if the lab handout specifies other thresholds.
MIN_F1=float(os.getenv("GATE_MIN_F1","0.50"))
MIN_SLICE_F1=float(os.getenv("GATE_MIN_SLICE_F1","0.35"))
MAX_P95_MS=float(os.getenv("GATE_MAX_P95_MS","1000"))
MAX_SIZE_MB=float(os.getenv("GATE_MAX_SIZE_MB","50"))

mlflow.set_tracking_uri(TRACKING)
client=MlflowClient()
exp=client.get_experiment_by_name(EXPERIMENT)
if exp is None: raise SystemExit("Experiment not found. Run train_lab3.py first.")
runs=client.search_runs([exp.experiment_id],order_by=["metrics.f1 DESC"])
if not runs: raise SystemExit("No candidate runs found.")
passed=[]
for r in runs:
 m=r.data.metrics
 checks={"overall_f1":m.get("f1",0)>=MIN_F1,"slice_le_12":m.get("f1_tenure_le_12",0)>=MIN_SLICE_F1,"slice_gt_12":m.get("f1_tenure_gt_12",0)>=MIN_SLICE_F1,"latency":m.get("p95_latency_ms",float("inf"))<=MAX_P95_MS,"size":m.get("model_size_mb",float("inf"))<=MAX_SIZE_MB}
 print(r.data.params.get("candidate",r.info.run_id),checks)
 if all(checks.values()): passed.append(r)
if not passed: raise SystemExit("PROMOTION BLOCKED: no candidate passed all gates. Review MLflow metrics.")
best=max(passed,key=lambda r:r.data.metrics["f1"])
model=mlflow.sklearn.load_model(f"runs:/{best.info.run_id}/model")
joblib.dump(model,OUT/"champion.joblib")
versions=client.search_model_versions(f"name='{MODEL_NAME}'")
matching=[v for v in versions if v.run_id==best.info.run_id]
if not matching: raise SystemExit("Registered model version for selected run was not found.")
version=max(matching,key=lambda v:int(v.version))
client.set_registered_model_alias(MODEL_NAME,"champion",version.version)
print(f"PROMOTED: {best.data.params.get('candidate')} | run={best.info.run_id} | version={version.version} | F1={best.data.metrics['f1']:.3f}")
print(f"Saved serving model: {OUT/'champion.joblib'}")
