import asyncio
import json
from websockets.asyncio.server import serve

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8000

rooms = {}
room_id = 1


async def handle_connection(websocket):
    async for message in websocket:
        data = json.loads(message)
        print("Received:", data)

        if data["action"] == "connect":
            response = join_room(data["host"], data["port"])
            await websocket.send(json.dumps(response))


def join_room(host, port):
    if room_id not in rooms:
        rooms[room_id] = []
    role = "leader" if len(rooms[room_id]) == 0 else "follower"
    rooms[room_id].append({"role": role, "host": host, "port": port})
    return {
        "room_id": room_id,
        "peers": rooms[room_id],
        "status": "connected"
    }


async def main():
    async with serve(handle_connection, SERVER_IP, SERVER_PORT) as server:
        print(f"Server running at ws://{SERVER_IP}:{SERVER_PORT}")
        await server.serve_forever()


asyncio.run(main())
