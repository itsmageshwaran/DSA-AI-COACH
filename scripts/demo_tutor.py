import asyncio
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    import websockets
except ImportError:
    print("Please install websockets: pip install websockets")
    sys.exit(1)

async def test_tutor(token: str):
    uri = f"ws://127.0.0.1:8000/api/v1/ws/tutor?token={token}"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")
            
            # Send a valid tutor message
            payload = {
                "action": "socratic_guide",
                "code": "def binary_search(arr, target):\n    pass",
                "execution_result": {"status": "success"},
                "ast_analysis": {"complexity": "O(1)"}
            }
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            await websocket.send(json.dumps(payload))

            # Read stream
            print("\n--- Receiving Stream ---")
            while True:
                try:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    if "error" in data:
                        print(f"\n[ERROR] {data['error']}")
                        break
                        
                    event = data.get("event")
                    if event == "stream_start":
                        print(f"\n[Stream Started: {data.get('action')}]")
                    elif event == "token":
                        print(data.get("chunk", ""), end="", flush=True)
                    elif event == "stream_end":
                        print("\n[Stream Ended]")
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed by server.")
                    break
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/demo_tutor.py <JWT_TOKEN>")
        sys.exit(1)
    
    token = sys.argv[1]
    asyncio.run(test_tutor(token))
