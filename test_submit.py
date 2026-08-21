import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

async def test_submit():
    async with httpx.AsyncClient() as client:
        print("Logging in...")
        login_res = await client.post(f"{BASE_URL}/auth/login", data={
            "username": "demo@kalvium.com",
            "password": "DemoPassword123!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Fetch current roadmap to get next problem
        print("Fetching next problem from roadmap...")
        rm_res = await client.get(f"{BASE_URL}/recommendations/next-problem", headers=headers)
        
        next_prob = rm_res.json()
        print("Next problem:", json.dumps(next_prob, indent=2))
        
        ex_id = next_prob.get("exercise_id")
        
        # We'll submit correct answer
        code = '''
def twoSum(nums, target):
    seen = {}
    for i, v in enumerate(nums):
        if target - v in seen:
            return [seen[target - v], i]
        seen[v] = i
    return []
'''

        print(f"\nSubmitting solution for {ex_id}...")
        res = await client.post(f"{BASE_URL}/execution/submit", headers=headers, json={
            "exercise_id": ex_id,
            "language": "python",
            "code": code
        })
        print("Submit Result:", json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(test_submit())
