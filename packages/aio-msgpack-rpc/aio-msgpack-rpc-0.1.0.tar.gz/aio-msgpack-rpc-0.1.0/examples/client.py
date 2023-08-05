import asyncio
import aio_msgpack_rpc


async def main():
    client = aio_msgpack_rpc.Client(*await asyncio.open_connection("localhost", 18002))

    # blocking rpc calls
    print("summing 1 & 2")
    result = await client.call("sum", 1, 2)
    print(f"result = {result}")
    assert result == 3

    # one way notifications
    print("sending notification 'hello'")
    client.notify("notification", "hello")

asyncio.get_event_loop().run_until_complete(main())