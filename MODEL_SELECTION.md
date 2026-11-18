# Model Selection and Promotion Policy

## Candidate models
The Lab 3 training pipeline evaluates three classifiers on the same stratified 80/20 train/test split (`random_state=42`): Logistic Regression, Random Forest, and Gradient Boosting. Each candidate uses the same preprocessing pipeline: standard scaling for numeric features and one-hot encoding for categorical features.

## Evaluation evidence
Each MLflow run records overall F1, ROC-AUC, F1 for customers with tenure `<= 12` months, F1 for customers with tenure `> 12` months, p95 single-row prediction latency, serialized model size, the dataset SHA-256, the model signature, and the Git commit SHA. The actual measured values are in the MLflow experiment `AI381-Lab3-Churn`; no performance values are hard-coded in this document.

## Promotion gates
A candidate is eligible only when all configured constraints pass:

- Overall F1 >= `GATE_MIN_F1` (default 0.50).
- F1 in each tenure slice >= `GATE_MIN_SLICE_F1` (default 0.35).
- p95 prediction latency <= `GATE_MAX_P95_MS` (default 1000 ms).
- Serialized model size <= `GATE_MAX_SIZE_MB` (default 50 MB).
- When a champion already exists, candidate F1 must exceed champion F1 by at least `GATE_MIN_F1_GAIN` (default 0.005).

Among eligible candidates, the highest-F1 candidate is promoted. If no candidate passes, or the candidate does not improve sufficiently over the current champion, promotion exits with `PROMOTION BLOCKED` and leaves the champion alias unchanged. The `GATE_FORCE_BLOCK=true` switch is provided solely to demonstrate a blocked run in the lab workflow.

## Selection rationale
The selection is evidence-driven rather than based on an assumed winner. The run with the highest F1 is selected only after passing both slice-level and operational constraints. The champion alias points to the registered MLflow model version, while `artifacts/champion_metadata.json` records its version, MLflow run ID, commit SHA, image tag, and F1 for deployment traceability.

## Reproducibility
The data split and candidate random seeds are fixed. The dataset hash and commit SHA are logged with every run so the training data and source revision can be identified later. For the CI promotion workflow, configure the GitHub Actions secret `MLFLOW_TRACKING_URI` (and credentials if required) to point to the same persistent MLflow tracking server that holds the champion registry.
