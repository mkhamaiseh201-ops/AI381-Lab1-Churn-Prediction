# AI381 Lab 3 – Quick Start (Option B: Local Docker Compose)

## Prerequisites
- Docker Desktop installed and running.
- Run commands from the repository root.

## Run the complete local workflow
```bash
docker compose -f docker-compose.lab3.yml up --build
```

The trainer runs three candidates, logs F1/AUC, F1 by tenure slice, p95 prediction latency and model size to MLflow, applies the promotion gate, registers the model and assigns the `champion` alias. The API starts after training and promotion complete.

Open:
- MLflow: http://localhost:5000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

Test prediction (PowerShell):
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/predict -ContentType 'application/json' -Body '{"tenure_months":5,"monthly_fee":89.9,"contract":"month-to-month","internet_service":"fiber","support_calls":3}'
```

Stop:
```bash
docker compose -f docker-compose.lab3.yml down
```

## Evidence to capture for the lab video
1. MLflow experiment showing three candidate runs and logged metrics.
2. Promotion-gate terminal output showing the selected candidate and registered version/`champion` alias.
3. API `/health` response and one successful `/predict` request.
4. GitHub Actions run after pushing the changes.

## Promotion gate defaults
`GATE_MIN_F1=0.50`, `GATE_MIN_SLICE_F1=0.35`, `GATE_MAX_P95_MS=1000`, `GATE_MAX_SIZE_MB=50`. If your official Lab 3 handout specifies different thresholds, use those exact values instead.
