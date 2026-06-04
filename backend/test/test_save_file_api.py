import os
from fastapi.testclient import TestClient
from save_file import app

client = TestClient(app)

def test_upload_unsupported_file():
    # Create a dummy text file in memory
    files = {"file": ("test.txt", b"dummy file content", "text/plain")}
    
    # Send a POST request to our FastAPI route
    response = client.post("/upload", files=files)
    
    # Assert protocol boundaries: Did it return 400 Bad Request?
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file type"

def test_analyze_metrics_missing_body():
    # Send an empty JSON body to the metrics endpoint
    response = client.post("/analyze/metrics", json={})
    
    # FastAPI should automatically reject this via Pydantic validation (422 Unprocessable Entity)
    assert response.status_code == 422
