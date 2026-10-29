from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Test 1: Health endpoint
def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Test 2: Prediction endpoint returns success
def test_predict_returns_success():
    customer = {
        "tenure_months": 12,
        "monthly_fee": 70.0,
        "support_calls": 2,
        "contract": "Month-to-month",
        "internet_service": "Fiber optic"
    }

    response = client.post("/predict", json=customer)

    assert response.status_code == 200


# Test 3: Prediction response schema
def test_predict_response_schema():
    customer = {
        "tenure_months": 12,
        "monthly_fee": 70.0,
        "support_calls": 2,
        "contract": "Month-to-month",
        "internet_service": "Fiber optic"
    }

    response = client.post("/predict", json=customer)
    data = response.json()

    assert response.status_code == 200
    assert "churn_probability" in data
    assert isinstance(data["churn_probability"], (int, float))
    assert 0 <= data["churn_probability"] <= 1


# Test 4: Missing input fields
def test_predict_missing_fields():
    customer = {
        "tenure_months": 12,
        "monthly_fee": 70.0
    }

    response = client.post("/predict", json=customer)

    assert response.status_code == 422


# Test 5: Deterministic prediction
def test_predict_is_deterministic():
    customer = {
        "tenure_months": 12,
        "monthly_fee": 70.0,
        "support_calls": 2,
        "contract": "Month-to-month",
        "internet_service": "Fiber optic"
    }

    first = client.post("/predict", json=customer)
    second = client.post("/predict", json=customer)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()