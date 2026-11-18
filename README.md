# AI381 Lab 3 – Tracked, Gated and Shipped Churn Prediction

**Course:** AI381 – Machine Learning Operations  
**Deployment choice:** Option B – Local Docker Compose  
**Repository:** https://github.com/mkhamaiseh201-ops/ai381-lab1-churn-prediction

## Overview

This repository extends the churn prediction API with MLflow experiment tracking, three candidate models, a quality/operations promotion gate, a registered `champion` model alias, and local Docker Compose deployment.

## Lab 3 components

- `src/train/train_lab3.py` – trains Logistic Regression, Random Forest, and Gradient Boosting candidates; logs metrics, dataset SHA-256, commit SHA, and model signature to MLflow.
- `src/train/promote_lab3.py` – applies overall and slice F1, p95 latency, model-size, and champion-improvement gates; registers/promotes only an eligible improved model.
- `MODEL_SELECTION.md` – documents candidate evaluation and the promotion policy.
- `docker-compose.lab3.yml` – starts MLflow, the training/promotion job, and the API.
- `docker-compose.deploy.yml` – runs the already-promoted champion API as a standalone deployment.
- `scripts/smoke_test.sh` – checks `/health` and `/predict`.
- `.github/workflows/ci.yml` – lint, tests, Lab 3 static validation, Docker build, Trivy scan, and GHCR publishing.
- `.github/workflows/train.yml` – starts an MLflow tracking server inside the GitHub Actions job, trains the three candidates, applies the promotion gate, and uploads the MLflow database/artifacts as workflow evidence. This CI server is job-scoped; the local Docker Compose MLflow volume is the persistent registry for the Option B demonstration.

## Local run – Option B

Run these commands from the repository root with Docker Desktop running:

```powershell
docker compose -f docker-compose.lab3.yml up --build
```

Open:

- MLflow UI: http://localhost:5000
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

Test the service in another PowerShell window:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

To stop the stack:

```powershell
docker compose -f docker-compose.lab3.yml down
```

## Deploy the promoted champion separately

After `artifacts/champion.joblib` and `artifacts/champion_metadata.json` have been created by a successful promotion:

```powershell
$env:COMMIT_SHA = (git rev-parse HEAD)
$env:IMAGE_TAG = $env:COMMIT_SHA
docker compose -f docker-compose.deploy.yml up --build -d
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

Stop deployment:

```powershell
docker compose -f docker-compose.deploy.yml down
```

## Promotion gate demonstration

The training workflow has a manual `force_block` input. Run it with `true` to demonstrate a deliberate blocked promotion. The expected result is a failed promotion step containing `PROMOTION BLOCKED`. Run normally with `false` to demonstrate training and promotion in the workflow's isolated MLflow server. The persistent local champion registry used for deployment is maintained by the Docker Compose MLflow volume.

## Traceability

The API `/health` response reports `model_version`, `mlflow_run_id`, `commit_sha`, and `image_tag`. These values are also stored in `artifacts/champion_metadata.json` and as MLflow model-version tags. CI image tags use the Git commit SHA.

## Submission evidence checklist

- [ ] MLflow shows three candidate runs and all required metrics/tags/signatures.
- [ ] `MODEL_SELECTION.md` is committed.
- [ ] A successful promotion and a deliberately blocked promotion are shown in GitHub Actions.
- [ ] Local deployed API returns healthy `/health` and successful `/predict` results.
- [ ] The API lineage fields match the promoted MLflow run and source commit.
- [ ] Record the required 5–8 minute video with face and voice, and upload the MP4 and `repo.txt` to the LMS/Teams location specified by the instructor.
