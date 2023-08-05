import msgpack
import asyncio
import logging
from typing import Any

from .error import RPCResponseError
from .request import RequestType

logger = logging.getLogger(__name__)


class Client(object):
    """RPC Client"""

    def __init__(self,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter,
                 *,
                 packer: msgpack.Packer = None,
                 unpacker: msgpack.Unpacker = None,
                 loop: asyncio.AbstractEventLoop=None,
                 response_timeout: int=None) -> None:
        self._reader = reader
        self._writer = writer
        self._packer = packer if packer is not None else msgpack.Packer(use_bin_type=True)
        self._unpacker = unpacker if unpacker is not None else msgpack.Unpacker(raw=False)
        self._loop = loop if loop is not None else asyncio.get_event_loop()

        # exposed state
        self.response_timeout = response_timeout

        # internal  mutable state
        self._next_msgid = 0
        self._pending_requests = {}
        self._receiver_task = None

    async def _receiver(self) -> None:
        """Background task to receive objects from the stream

        This allows parallel/overlapping rpc calls
        """
        try:
            unpacker = self._unpacker
            reader = self._reader
            logger.info("starting receiver")
            while len(self._pending_requests):
                data = await reader.read(n=2048)
                if not data:
                    raise ConnectionError("Connection has been closed")
                unpacker.feed(data)
                for obj in unpacker:
                    self._on_recv(obj)
        except asyncio.CancelledError:
            pass
        except ConnectionError:
            logger.info("Server connection has closed")
        except Exception as e:
            logger.exception("exception in client receiver")
        finally:
            logging.info("ending receiver")

    def close(self) -> None:
        """Remove all pending responses and close the underlying connection"""
        self._pending_requests = {}
        self._writer.close()

        if self._receiver_task is not None:
            self._receiver_task.cancel()

    def _on_recv(self, obj) -> None:
        """Handler for the reception of msgpack objects"""
        try:
            if obj[0] == RequestType.RESPONSE:
                _, msgid, error, result = obj
                _, future = self._pending_requests[msgid]
                if error:
                    future.set_exception(RPCResponseError(error))
                else:
                    future.set_result(result)
            else:
                logger.error("received non-response object %r", obj)
        except LookupError as e:
            logger.error("received unknown object type %r", obj)

    def _get_next_msgid(self) -> int:
        """return the next msgid to be used"""
        val = self._next_msgid
        self._next_msgid = (self._next_msgid + 1) & 0xFFFFFFFF
        return val

    async def call(self, name: str, *args, timeout: float=None) -> Any:
        """Call a remote function

        If timeout is not given the class attribute response_timeout will be used.
        """
        logger.debug("call: %s%r", name, *args)
        timeout = timeout if timeout is not None else self.response_timeout

        request = (RequestType.REQUEST, self._get_next_msgid(), name, args)

        # create a future for the response and make it responsable for its own cleanup
        future_response = asyncio.Future()
        self._pending_requests[request[1]] = (request, future_response)
        future_response.add_done_callback(lambda fut: self._pending_requests.pop(request[1]))

        self._writer.write(self._packer.pack(request))

        # start the receiver if its not already active
        if self._receiver_task is None or self._receiver_task.done():
            self._receiver_task = self._loop.create_task(self._receiver())
        # wait for the future or the timeout to complete
        return await asyncio.wait_for(future_response, timeout=timeout, loop=self._loop)

    def notify(self, name: str, *args: Any) -> asyncio.Future:
        """Send a one-way notification to the server

        This function returns a future which is resolved when the write buffer is flushed.
        This can be optionally awaited on to ensure themessage has been sent.
        """
        logger.debug("notify: %s%r", name, *args)
        request = (RequestType.NOTIFY, name, args)
        self._writer.write(self._packer.pack(request))
        return self._writer.drain()
