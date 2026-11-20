import asyncio
import argparse
import json

from websockets.asyncio.client import connect

SERVER_URI = "ws://127.0.0.1:8000"


async def main(host, port):
    async with connect(SERVER_URI) as websocket:
        await websocket.send(json.dumps(
            {
                "action": "connect",
                "host": host,
                "port": port
            }
        ))

        response = await websocket.recv()
        print(response)

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

asyncio.run(main(args.host, args.port))
