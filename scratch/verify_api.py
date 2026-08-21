import httpx
import sys
import uuid

BASE_URL = "http://localhost:8000"
test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
test_password = "Password123!"

def run_tests():
    print("=== PHASE 3: BACKEND API VERIFICATION ===")
    
    # 1. Health
    r = httpx.get(f"{BASE_URL}/api/v1/health")
    print(f"GET /api/v1/health: {r.status_code}")
    assert r.status_code == 200

    # 2. Register
    r = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": test_email,
        "password": test_password,
        "full_name": "Test User"
    })
    print(f"POST /api/v1/auth/register: {r.status_code}")
    assert r.status_code in [200, 201]

    # 3. Login
    r = httpx.post(f"{BASE_URL}/api/v1/auth/login", data={
        "username": test_email,
        "password": test_password
    })
    print(f"POST /api/v1/auth/login: {r.status_code}")
    assert r.status_code == 200
    token = r.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}

    # 4. GET /api/v1/users/me
    r = httpx.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
    print(f"GET /api/v1/users/me: {r.status_code}")
    assert r.status_code == 200

    # 5. GET /api/v1/learning-paths
    r = httpx.get(f"{BASE_URL}/api/v1/learning-paths", headers=headers)
    print(f"GET /api/v1/learning-paths: {r.status_code} - count: {len(r.json())}")
    assert r.status_code == 200

    # 6. GET /api/v1/progress/summary
    r = httpx.get(f"{BASE_URL}/api/v1/progress/summary", headers=headers)
    print(f"GET /api/v1/progress/summary: {r.status_code}")
    if r.status_code != 200:
        print(r.text)

    # 7. GET /api/v1/exercises
    r = httpx.get(f"{BASE_URL}/api/v1/exercises", headers=headers)
    print(f"GET /api/v1/exercises: {r.status_code} - count: {len(r.json())}")
    assert r.status_code == 200

    # 8. GET /api/v1/billing/quota
    r = httpx.get(f"{BASE_URL}/api/v1/billing/quota", headers=headers)
    print(f"GET /api/v1/billing/quota: {r.status_code}")
    if r.status_code != 200:
        print(r.text)

    # 9. GET /api/v1/billing/organizations
    r = httpx.get(f"{BASE_URL}/api/v1/billing/organizations", headers=headers)
    print(f"GET /api/v1/billing/organizations: {r.status_code}")
    if r.status_code != 200:
        print(r.text)

    # 10. GET /api/v1/learning-intelligence/recommendations
    r = httpx.get(f"{BASE_URL}/api/v1/learning-intelligence/recommendations", headers=headers)
    print(f"GET /api/v1/learning-intelligence/recommendations: {r.status_code}")
    if r.status_code != 200:
        print(r.text)

    print("=== API VERIFICATION COMPLETED ===")

if __name__ == "__main__":
    run_tests()
