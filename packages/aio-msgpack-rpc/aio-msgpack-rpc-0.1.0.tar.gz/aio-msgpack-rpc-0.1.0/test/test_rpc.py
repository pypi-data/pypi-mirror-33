import asyncio
import pytest
import msgpack

import aio_msgpack_rpc


@pytest.mark.asyncio
async def test_basic_request(make_pair):
    class Server:
        async def sum(self, x, y):
            return x + y

    async with make_pair(Server()) as (server, client):
        result = await client.call("sum", 2, 4)
        assert result == 6


@pytest.mark.asyncio
async def test_server_error(make_pair):
    class Server:
        async def error(self, x):
            raise ValueError("some error")

    async with make_pair(Server()) as (server, client):
        with pytest.raises(aio_msgpack_rpc.error.RPCResponseError):
            await client.call("error", 10, timeout=1)


@pytest.mark.asyncio
async def test_notify(make_pair):
    event = asyncio.Event()

    class Server:
        def notification(self, x):
            event.set()

    async with make_pair(Server()) as (server, client):
        client.notify("notification", 10)
        await asyncio.wait_for(event.wait(), timeout=1)


@pytest.mark.asyncio
async def test_msgpack_streaming(make_pair):
    event = asyncio.Event()

    class Server:
        def foo(self, x):
            event.set()

    async with make_pair(Server()) as (server, client):
        data = msgpack.packb([aio_msgpack_rpc.request.RequestType.NOTIFY, "foo", [10]])
        client._writer.write(data[:len(data) // 2])
        await client._writer.drain()
        await asyncio.sleep(0.3)
        client._writer.write(data[len(data) // 2:])
        await client._writer.drain()
        await asyncio.wait_for(event.wait(), timeout=1)


@pytest.mark.asyncio
async def test_async_call_handler(make_pair):
    class Server:
        async def foo(self, x):
            await asyncio.sleep(0.1)
            return x

    async with make_pair(Server()) as (server, client):
        result = await client.call("foo", 10)
        assert result == 10


@pytest.mark.asyncio
async def test_plain_call_handler(make_pair):
    class Server:
        def foo(self, x):
            return x

    async with make_pair(Server()) as (server, client):
        result = await client.call("foo", 10)
        assert result == 10


@pytest.mark.asyncio
async def test_async_notify_handler(make_pair):
    event = asyncio.Event()

    class Server:
        async def notification(self, x):
            await asyncio.sleep(0.1)
            event.set()

    async with make_pair(Server()) as (server, client):
        client.notify("notification", 10)
        await event.wait()


@pytest.mark.asyncio
async def test_plain_notify_handler(make_pair):
    event = asyncio.Event()

    class Server:
        def notification(self, x):
            event.set()

    async with make_pair(Server()) as (server, client):
        client.notify("notification", 10)
        await event.wait()
