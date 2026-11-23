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
        self.role = None  # leader, follower

        # List of peers in the same room (role, host, port, peer_id)
        self.peers = []
        self.status = "connecting"  # connecting, connected, disconnected
        self.connections = {}  # peer_id -> websocket connection
        self.game_state = {
            "sequence_number": 0,
            "players": {},
            "snowballs": [],
        }

    def add_player(self, peer_id):
        self.game_state["players"][str(peer_id)] = {
            "x": 100,
            "y": 100,
            "hearts": 3,
            "score": 0,
            "state": "playing",
        }

    async def receive_messages(self, websocket):
        async for message in websocket:
            data = json.loads(message)
            print("Received:", data)

            if data["action"] == "hello":
                peer_id = data["peer_id"]
                self.connections[peer_id] = websocket

                if self.role == "leader":
                    self.add_player(peer_id)
                    self.game_state["sequence_number"] += 1
                    await self.broadcast_game_state()

            elif data["action"] == "update":
                if self.role == "follower":
                    self.game_state = data["game_state"]
                    print("Game state:", self.game_state)

    async def broadcast_game_state(self):
        message = json.dumps({
            "action": "update",
            "game_state": self.game_state,
        })

        for websocket in self.connections.values():
            await websocket.send(message)

    async def connect_to_peer(self, peer):
        address = f"ws://{peer['host']}:{peer['port']}"

        async with connect(address) as websocket:
            self.connections[peer["peer_id"]] = websocket

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
                self.status = "connected"

                if self.role == "leader":
                    self.add_player(self.peer_id)

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
