import time
import msgpackrpc
import multiprocessing

NUM_CALLS = 10000


def run_sum_server():
    class SumServer(object):
        def sum(self, x, y):
            return x + y

    server = msgpackrpc.Server(SumServer())
    server.listen(msgpackrpc.Address("localhost", 6000))
    server.start()


def call():
    client = msgpackrpc.Client(msgpackrpc.Address("localhost", 6000))

    start = time.time()
    for _ in range(NUM_CALLS):
        client.call('sum', 1, 2)

    print('call: %d qps' % (NUM_CALLS / (time.time() - start)))
    client.close()


def call_async():
    client = msgpackrpc.Client(msgpackrpc.Address("localhost", 6000))

    start = time.time()
    for _ in range(NUM_CALLS):
        future = client.call_async('sum', 1, 2)
        future.get()

    print('call_async: %d qps' % (NUM_CALLS / (time.time() - start)))
    client.close()


def main():
    p = multiprocessing.Process(target=run_sum_server)
    p.start()

    time.sleep(1)

    call()

    time.sleep(1)

    call_async()

    p.terminate()


if __name__ == '__main__':
    main()