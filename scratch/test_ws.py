import asyncio
import httpx
import websockets
import json

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Register
        res = await client.post('http://127.0.0.1:8000/api/v1/auth/register', json={
            'email': 'ws_test4@example.com',
            'password': 'password123',
            'full_name': 'WS Test'
        })
        if res.status_code != 200 and res.status_code != 201:
            print("Register failed:", res.status_code, res.text)
            res = await client.post('http://127.0.0.1:8000/api/v1/auth/login', data={
                'username': 'ws_test4@example.com',
                'password': 'password123'
            })
        print(res.json())
        token = res.json().get('access_token')
        
        # 2. Connect WS
        ws_url = f'ws://127.0.0.1:8000/api/v1/ws/tutor?token={token}'
        print(f'Connecting to {ws_url}')
        try:
            async with websockets.connect(ws_url) as ws:
                print('Connected!')
                await ws.send(json.dumps({"action": "complexity_analyst", "code": "pass"}))
                msg = await ws.recv()
                print('Received:', msg)
        except Exception as e:
            print('WS Error:', type(e), e)

asyncio.run(main())
