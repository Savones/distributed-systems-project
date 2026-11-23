import asyncio
import argparse
import json

from websockets.asyncio.client import connect
from websockets.asyncio.server import serve


SERVER_URI = "ws://127.0.0.1:8000"


class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peer_id = None
        self.room_id = None
        self.role = None
        self.peers = []

    async def receive_messages(self, websocket):
        async for message in websocket:
            print("Received:", message)

    async def connect_to_peer(self, peer):
        address = f"ws://{peer['host']}:{peer['port']}"

        async with connect(address) as websocket:
            await websocket.send(json.dumps({
                "action": "hello",
                "peer_id": self.peer_id,
            }))
            await self.receive_messages(websocket)

    async def run(self):
        async with serve(self.receive_messages, self.host, self.port):
            async with connect(SERVER_URI) as websocket:
                await websocket.send(json.dumps({
                    "action": "connect",
                    "host": self.host,
                    "port": self.port,
                }))

                response = json.loads(await websocket.recv())
                print(response)

                self.peer_id = response["peer_id"]
                self.room_id = response["room_id"]
                self.role = response["role"]
                self.peers = response["peers"]

                tasks = [self.receive_messages(websocket)]

                for peer in self.peers:
                    tasks.append(self.connect_to_peer(peer))

                await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()

    peer = Peer(args.host, args.port)
    asyncio.run(peer.run())
