from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import os

from main import app
from database import get_db, Base

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_certificates.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Cleanup test images
    if os.path.exists("generated_certificates"):
        for f in os.listdir("generated_certificates"):
            os.remove(os.path.join("generated_certificates", f))

def test_input_validation():
    response = client.post("/api/jobs", json={"recipients": []}) # empty list
    assert response.status_code == 422 
    
    response = client.post("/api/jobs", json={"recipients": [{"recipient_name": ""}]}) # Missing course
    assert response.status_code == 422

def test_bulk_generation_and_status():
    payload = {
        "recipients": [
            {"recipient_name": "Alice", "course_name": "Python 101"},
            {"recipient_name": "FAIL_ME", "course_name": "Failure 101"}, # Intentional fail
            {"recipient_name": "Bob", "course_name": "Python 101"}
        ]
    }
    
    # 1. Create Job
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 202
    job_id = response.json()["id"]
    
    # Fast-forward background tasks by calling the endpoint directly in TestClient waits for them to complete synchronously 
    
    # 2. Check Job Status
    status_response = client.get(f"/api/jobs/{job_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["status"] == "completed"
    
    # 3. Check Individual Failure Handling
    certs = data["certificates"]
    assert len(certs) == 3
    
    alice_cert = next(c for c in certs if c["recipient_name"] == "Alice")
    assert alice_cert["status"] == "generated"
    
    fail_cert = next(c for c in certs if c["recipient_name"] == "FAIL_ME")
    assert fail_cert["status"] == "failed"
    assert "Simulated generation failure" in fail_cert["error_message"]
    
    # Bob should still be generated despite FAIL_ME failing
    bob_cert = next(c for c in certs if c["recipient_name"] == "Bob")
    assert bob_cert["status"] == "generated"

    # 4. Retrieve Certificate
    download_response = client.get(f"/api/certificates/{alice_cert['id']}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "image/png"