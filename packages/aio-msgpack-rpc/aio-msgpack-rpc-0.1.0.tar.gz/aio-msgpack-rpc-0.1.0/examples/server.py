import asyncio
import aio_msgpack_rpc


# handlers can be defined on a class
# they can either be async or plain functions
class MyServicer:
    async def sum(self, x, y):
        print(f"sum: {x}, {y}")
        return x + y

    def notification(self, msg):
        print(f"notification: {msg}")


async def main():
    try:
        server = await asyncio.start_server(aio_msgpack_rpc.Server(MyServicer()), host="localhost", port=18002)

        while True:
            await asyncio.sleep(0.1)
    finally:
        server.close()

try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    pass