import asyncio
import json

from websockets.asyncio.server import serve


class MatchmakingServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.rooms = {}
        self.room_id = 1
        self.next_peer_id = 1

    async def handle_connection(self, websocket):
        async for message in websocket:
            data = json.loads(message)
            print("Received:", data)

            if data["action"] == "connect":
                response = self.join_room(data["host"], data["port"])
                await websocket.send(json.dumps(response))

    def join_room(self, host, port):
        if self.room_id not in self.rooms:
            self.rooms[self.room_id] = []

        room = self.rooms[self.room_id]
        existing_peers = room.copy()
        role = "leader" if len(room) == 0 else "follower"

        peer = {
            "role": role,
            "host": host,
            "port": port,
            "peer_id": self.next_peer_id,
        }

        room.append(peer)
        self.next_peer_id += 1

        return {
            "room_id": self.room_id,
            "role": role,
            "peer_id": peer["peer_id"],
            "peers": existing_peers,
        }

    async def run(self):
        async with serve(
            self.handle_connection, self.host, self.port
        ) as server:
            print(f"Server running at ws://{self.host}:{self.port}")
            await server.serve_forever()


if __name__ == "__main__":
    server = MatchmakingServer("127.0.0.1", 8000)
    asyncio.run(server.run())
