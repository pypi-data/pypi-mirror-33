import pytest
import asyncio
import asyncio_extras

import aio_msgpack_rpc


@pytest.fixture
def make_pair():
    @asyncio_extras.async_contextmanager
    async def maker(server):
        server = await asyncio.start_server(aio_msgpack_rpc.Server(server), host="localhost", port=18002)
        client = aio_msgpack_rpc.Client(*(await asyncio.open_connection("localhost", 18002)))
        yield server, client
        server.close()
        client.close()
        await server.wait_closed()
        await asyncio.sleep(0.1)
    return maker
