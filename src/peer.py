import asyncio
import argparse
import json

from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

from ui import GameUI
from variables import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_RADIUS

SERVER_URI = "ws://127.0.0.1:8000"


class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peer_id = None
        self.room_id = None
        self.role = None  # leader, follower
        self.leader = None  # leader peer info
        self.ui = GameUI()

        self.peers = []
        self.status = "connecting"
        self.connections = {}  # peer_id -> websocket connection

        self.game_state = {
            "sequence_number": 0,
            "players": {},
            "snowballs": [],
        }

    def log(self, message):
        print(
            f"[Peer {self.peer_id} | {self.role}] {message}",
            flush=True,
        )

    def print_game_state(self):
        print(
            f"\n--- Peer {self.peer_id} | {self.role} "
            f"| Update #{self.game_state['sequence_number']} ---"
        )
        print(
            f"{'Player':<12}"
            f"{'X':<8}"
            f"{'Y':<8}"
            f"{'Hearts':<10}"
            f"{'Score':<10}"
            f"{'State'}"
        )

        for peer_id, player in self.game_state["players"].items():
            label = (
                f"{peer_id} (you)"
                if peer_id == str(self.peer_id)
                else peer_id
            )

            print(
                f"{label:<12}"
                f"{player['x']:<8}"
                f"{player['y']:<8}"
                f"{player['hearts']:<10}"
                f"{player['score']:<10}"
                f"{player['state']}"
            )

        print("-" * 60, flush=True)

    async def submit_player_input(self, peer_id, x, y):
        player_input = {"x": x, "y": y}

        if self.role == "leader":
            await self.handle_player_input(self.peer_id, player_input)

        elif self.leader is not None:
            await self.leader.send(json.dumps({
                "action": "input",
                "input": player_input,
            }))

    def process_input(self, peer_id, player_input):
        player = self.game_state["players"][str(peer_id)]

        if player["state"] != "playing":
            return

        x = max(
            PLAYER_RADIUS,
            min(player_input["x"], SCREEN_WIDTH - PLAYER_RADIUS),
        )

        y = max(
            PLAYER_RADIUS,
            min(player_input["y"], SCREEN_HEIGHT - PLAYER_RADIUS),
        )

        for other_id, other in self.game_state["players"].items():
            if other_id == str(peer_id) or other["state"] != "playing":
                continue

            distance_squared = (
                (x - other["x"]) ** 2
                + (y - other["y"]) ** 2
            )

            if distance_squared < (PLAYER_RADIUS * 2) ** 2:
                return

        player["x"] = x
        player["y"] = y

    def add_player(self, peer_id):
        self.game_state["players"][str(peer_id)] = {
            "x": 100,
            "y": 100,
            "hearts": 3,
            "score": 0,
            "state": "playing",
        }

        self.log(f"Added player {peer_id} to the game")

    async def receive_messages(self, websocket):
        sender_id = None

        async for message in websocket:
            data = json.loads(message)

            if data["action"] == "hello":
                sender_id = data["peer_id"]
                self.connections[sender_id] = websocket
                self.log(f"Received hello from peer {sender_id}")

                if self.role == "leader":
                    self.add_player(sender_id)
                    self.game_state["sequence_number"] += 1
                    await self.broadcast_game_state()

            elif data["action"] == "input":
                if self.role == "leader" and sender_id is not None:
                    await self.handle_player_input(
                        sender_id, data["input"]
                    )

            elif data["action"] == "update":
                if self.role == "follower":
                    self.game_state = data["game_state"]
                    self.log(
                        f"Received update "
                        f"#{self.game_state['sequence_number']}"
                    )
                    self.print_game_state()

    async def handle_player_input(self, peer_id, player_input):
        source = (
            "own player"
            if peer_id == self.peer_id
            else f"peer {peer_id}"
        )
        self.log(f"Processing input from {source}: {player_input}")

        self.process_input(peer_id, player_input)
        self.game_state["sequence_number"] += 1
        await self.broadcast_game_state()

    async def broadcast_game_state(self):
        sequence_number = self.game_state["sequence_number"]

        message = json.dumps({
            "action": "update",
            "game_state": self.game_state,
        })

        # Copy the connections before sending.
        connections = list(self.connections.values())

        self.log(
            f"Broadcasting update #{sequence_number} "
            f"to {len(connections)} peer(s)"
        )
        self.print_game_state()

        for websocket in connections:
            await websocket.send(message)

    async def connect_to_peer(self, peer):
        address = f"ws://{peer['host']}:{peer['port']}"

        async with connect(address) as websocket:
            self.connections[peer["peer_id"]] = websocket
            self.log(
                f"Connected to peer {peer['peer_id']} at {address}"
            )

            await websocket.send(json.dumps({
                "action": "hello",
                "peer_id": self.peer_id,
            }))

            if peer["role"] == "leader":
                self.leader = websocket
                await asyncio.gather(
                    self.receive_messages(websocket)
                )
            else:
                await self.receive_messages(websocket)

    async def run(self):
        async with serve(self.receive_messages, self.host, self.port):
            print(
                f"Listening at ws://{self.host}:{self.port}",
                flush=True,
            )

            async with connect(SERVER_URI) as websocket:
                await websocket.send(json.dumps({
                    "action": "connect",
                    "host": self.host,
                    "port": self.port,
                }))

                response = json.loads(await websocket.recv())

                self.peer_id = response["peer_id"]
                self.room_id = response["room_id"]
                self.role = response["role"]
                self.peers = response["peers"]
                self.status = "connected"

                self.log(
                    f"Joined room {self.room_id} "
                    f"at {self.host}:{self.port}"
                )
                tasks = [self.receive_messages(websocket)]
                if self.role == "leader":
                    self.add_player(self.peer_id)
                    self.print_game_state()

                tasks.append(self.ui.run(self))

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
