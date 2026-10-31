AI381 Lab 2 – Churn Prediction API

Course: AI381 – Machine Learning Operations
University: Jordan University of Science and Technology (JUST)
Instructor: Dr. Tariq Al-Omari

CI Status

Project Overview

This project packages a customer churn prediction model as a FastAPI service. It includes automated tests, Docker containerization, and a GitHub Actions CI/CD workflow.

Project Structure

* src/train/train.py – Model training script.
* src/app/main.py – FastAPI application.
* tests/ – Automated tests.
* Dockerfile – Multi-stage Docker build with a non-root runtime user and health check.
* .github/workflows/ci.yml – Automated testing, image build, Trivy scan, and publishing to GHCR.

Run with Docker

Build and start the container:

docker build -t ai381-churn .
docker run -d --name ai381-churn -p 8000:8000 ai381-churn

API Endpoints

* GET /health – Checks service health.
* POST /predict – Returns a churn prediction.

Open the API documentation at:

http://localhost:8000/docs

Automated Testing

Run the tests locally:

python -m pytest -v

CI/CD Pipeline

GitHub Actions automatically runs tests on pull requests and pushes to main. On pushes to main, it builds the Docker image, scans it with Trivy, and publishes it to GitHub Container Registry (GHCR), tagged with the commit SHA.

Container Registry

Docker images are published to:

ghcr.io/mkhamaiseh201-ops/ai381-lab1-churn-prediction

Repository

GitHub Repository
Docker Image Digest

The Docker image was successfully built, scanned with Trivy, and pushed to GitHub Container Registry (GHCR).

Published Image Digest:

ghcr.io/mkhamaiseh201-ops/ai381-lab1-churn-prediction@sha256:7b1b8cf2e46e5d873b615dd8c15d8534a393e98554dbcd558b8b837454b87081
