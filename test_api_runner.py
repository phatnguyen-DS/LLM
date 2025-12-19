import sys
import os

# Put backend in path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from fastapi.testclient import TestClient
try:
    from backend.api import app
except ImportError:
    # Fallback if running from within backend dir or other issue
    from api import app

def run_tests():
    # Use context manager to trigger startup/shutdown events
    with TestClient(app) as client:
        print("Testing /health ...")
        response = client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        print("\nTesting /predict ...")
        text = "Thẻ của tôi bị khóa không lý do"
        response = client.post("/predict", json={"text": text})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    run_tests()
