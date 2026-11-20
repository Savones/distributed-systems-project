import asyncio
from websockets.asyncio.server import serve


async def handle_connection(websocket):
    async for message in websocket:
        print("Received:", message)
        await websocket.send("Hello - server here")


async def main():
    async with serve(handle_connection, "127.0.0.1", 8000) as server:
        print("Server running at ws://127.0.0.1:8000")
        await server.serve_forever()


asyncio.run(main())
