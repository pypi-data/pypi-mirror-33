import time
import asyncio
import multiprocessing
import aio_msgpack_rpc
import tornado

import logging


NUM_CALLS = 10000


def run_sum_server():
    class MyServer(object):
        def notification(self, x, y):
            return x + y

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(aio_msgpack_rpc.Server(MyServer()), 'localhost', 6000)
    loop.run_until_complete(coro)
    loop.run_forever()


def call():
    async def do():
        reader, writer = await asyncio.open_connection("localhost", 6000)
        client = aio_msgpack_rpc.Client(reader, writer)
        for i in range(NUM_CALLS):
            await client.notify("notification", 1, 2)
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do())
    print('call: %d qps' % (NUM_CALLS / (time.time() - start)))


def main():
    p = multiprocessing.Process(target=run_sum_server)
    p.start()

    time.sleep(1)

    call()

    p.terminate()

if __name__ == '__main__':
    main()