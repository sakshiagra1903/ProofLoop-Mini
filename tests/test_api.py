from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["api"] == "healthy"

def test_path_traversal_rejected_by_schema():
    response = client.post("/api/tasks", json={"task": "Create a sales report", "operation": "sales_report", "input_file": "../secret.csv", "output_file": "report.json", "max_retries": 0})
    assert response.status_code == 422

def test_unknown_task_is_404():
    response = client.get("/api/tasks/not-a-real-task")
    assert response.status_code == 404

def test_dashboard_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "Automation you can" in response.text

def test_analytics_shape():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    payload = response.json()
    assert {"total_tasks", "verified_tasks", "failed_tasks", "success_rate", "verification_checks", "rows_processed", "duplicates_removed"}.issubset(payload)

def test_workspace_file_listing():
    response = client.get("/api/files")
    assert response.status_code == 200
    assert isinstance(response.json()["files"], list)
