import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

async def test_execution():
    async with httpx.AsyncClient() as client:
        print("Logging in...")
        login_res = await client.post(f"{BASE_URL}/auth/login", data={
            "username": "demo@kalvium.com",
            "password": "DemoPassword123!"
        })
        if login_res.status_code != 200:
            print("Login failed!", login_res.text)
            return
            
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("Testing correct submission via /execution/run...")
        res = await client.post(f"{BASE_URL}/execution/run", headers=headers, json={
            "language": "python",
            "code": "def twoSum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]",
            "entrypoint": "twoSum",
            "test_cases": [
                {"input_data": {"nums": [2, 7, 11, 15], "target": 9}, "expected_output": [0, 1]}
            ]
        })
        print("Run Result:", json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(test_execution())
