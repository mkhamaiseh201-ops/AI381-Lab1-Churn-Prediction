AI381 Lab 3 – Tracked, Gated and Shipped

Course: AI381 – Machine Learning Operations
University: Jordan University of Science and Technology (JUST)
Instructor: Dr. Tariq Al-Omari
Lab: 3 – Tracked, Gated and Shipped
Deployment Option: Option B – Local Docker Compose

1. Project Overview

This project extends the Lab 2 Customer Churn Prediction API by introducing MLflow experiment tracking, model comparison, model promotion, and containerized deployment.

The main objective is to make model training reproducible, select a suitable champion model, and serve it through a Docker-based API.

2. Technologies Used

* Python
* Scikit-learn
* MLflow
* FastAPI
* Docker
* Docker Compose
* GitHub Actions
* GitHub Container Registry (GHCR)

3. Project Components

* src/train/ – Model training scripts.
* src/app/main.py – FastAPI prediction service.
* tests/ – Automated tests.
* Dockerfile.lab3 – Lab 3 Docker image.
* docker-compose.lab3.yml – Lab 3 Docker Compose configuration.
* requirements-docker.txt – Application dependencies.
* requirements-lab3.txt – Lab 3 dependencies.
* .github/workflows/ci.yml – GitHub Actions CI workflow.

4. MLflow Experiment Tracking

MLflow is used to track model training experiments and store model-related information.

The tracking process includes:

* Model parameters.
* Evaluation metrics.
* Training experiment information.
* Model artifacts.
* Model versions and champion alias.

MLflow UI:

http://localhost:5000

5. Model Training and Selection

Three candidate models are evaluated:

* Logistic Regression
* Random Forest
* Gradient Boosting

The models are compared using evaluation metrics, including F1-score.

The selected model is promoted as the champion model according to the promotion process.

6. Model Registry and Promotion

The MLflow Model Registry stores model versions and identifies the selected model using the champion alias.

The promotion process evaluates candidate models before selecting a model for serving.

7. Deployment – Option B

The project uses local Docker Compose deployment.

Start the Lab 3 services:

docker compose -f docker-compose.lab3.yml up -d --build

Check running services:

docker compose -f docker-compose.lab3.yml ps

The prediction API is available at:

http://localhost:8000

API documentation:

http://localhost:8000/docs

8. API Endpoints

* GET /health – Checks API health.
* POST /predict – Returns a customer churn prediction.

9. GitHub Actions

GitHub Actions automates repository validation and Docker image build, security scanning, and publishing to GitHub Container Registry.

The workflow includes:

* Lint and Test.
* Lab 3 validation.
* Docker image build.
* Trivy security scan.
* GHCR publishing.

10. Model Traceability

The project aims to connect the deployed Docker image with its Git commit and the corresponding MLflow training run.

This provides traceability for identifying the model version used by the running service.

11. Repository

GitHub Repository:

https://github.com/mkhamaiseh201-ops/ai381-lab1-churn-prediction

12. Deployment Choice

This project uses Option B – Local Docker Compose, as permitted by the Lab 3 instructions. This option provides the required local deployment path without requiring Azure Container Apps.
