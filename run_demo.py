import json
import urllib.request
import urllib.parse
import subprocess
import time

def run():
    print("1. Registering user...")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/auth/register",
        data=json.dumps({
            "email": f"demo_{int(time.time())}@example.com",
            "password": "SecurePassword123!"
        }).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        if e.code != 400: # 400 if already registered, which is fine
            print(f"Failed to register: {e.read()}")
            return
            
    print("2. Logging in...")
    data = urllib.parse.urlencode({
        "username": json.loads(req.data)["email"],
        "password": "SecurePassword123!"
    }).encode()
    
    login_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    try:
        with urllib.request.urlopen(login_req) as response:
            res_data = json.loads(response.read())
            token = res_data["access_token"]
            print("Successfully obtained JWT token.")
            
            print("3. Running demo_tutor.py script...")
            subprocess.run(["python", "scripts/demo_tutor.py", token])
            
    except Exception as e:
        print(f"Failed to login or run demo: {e}")

if __name__ == "__main__":
    run()
