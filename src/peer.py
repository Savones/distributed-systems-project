import asyncio
from websockets.asyncio.client import connect


async def main():
    async with connect("ws://127.0.0.1:8000") as websocket:
        await websocket.send("Hello - peer here")

        response = await websocket.recv()
        print(response)


asyncio.run(main())
