import asyncio
import argparse
import json

from websockets.asyncio.client import connect
from websockets.asyncio.server import serve


SERVER_URI = "ws://127.0.0.1:8000"


async def receive_messages(websocket):
    async for message in websocket:
        print("Received:", message)


async def connect_to_peer(peer):
    address = f"ws://{peer['host']}:{peer['port']}"

    async with connect(address) as websocket:
        await websocket.send(json.dumps({"action": "hello"}))
        await receive_messages(websocket)


async def main(host, port):
    async with serve(receive_messages, host, port):
        async with connect(SERVER_URI) as websocket:
            await websocket.send(json.dumps({
                "action": "connect",
                "host": host,
                "port": port
            }))

            response = json.loads(await websocket.recv())
            print(response)

            tasks = [receive_messages(websocket)]

            for peer in response["peers"]:
                tasks.append(connect_to_peer(peer))

            await asyncio.gather(*tasks)


# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

asyncio.run(main(args.host, args.port))
