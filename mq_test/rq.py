"""RabbitMQ implementation."""
# 1. std
from typing import Optional
# 2. 3rd
import pika
# 3. local
from bq import SQ, SQC, AQ, AQC


# == Sync ==
class _RSQ(SQ):
    """RabbitMQ Sync Queue.
    [RTFM](https://pika.readthedocs.io/en/stable/index.html)
    """
    _master: 'RSQC'
    # conn: pika.BlockingConnection  # Plan C
    chan: pika.adapters.blocking_connection.BlockingChannel
    __q: str

    def __init__(self, master: 'RSQC', __id: int):
        super().__init__(master, __id)
        self.__q = f"{__id:04d}"
        # TODO: self.channel.queue_declare(queue=kju, passive=True) to chk queue exists

    def open(self):
        self.chan = self._master.chan  # Plan A
        # self.chan = self._master.conn.channel()  # Plan B
        # self.chan.basic_qos(prefetch_count=1)  # Plan B

    def count(self) -> int:
        return self.chan.queue_declare(queue=self.__q, passive=True).method.message_count

    def put(self, data: bytes):
        self.chan.basic_publish(
            exchange='',
            routing_key=self.__q,
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
            body=data
        )

    def get(self, wait: bool = True) -> Optional[bytes]:  # FIXME: allwas no_wait
        method_frame, header_frame, body = self.chan.basic_get(self.__q, auto_ack=True)
        # or ... = channel.consume(kju): generator
        if method_frame:
            return body

    def close(self):
        ...
        # self.chan.close()  # Plan B
        # self.conn.close()  # Plan C


class RSQC(SQC):
    """RabbitMQ Sync Queue Container."""
    _child_cls = _RSQ
    host: str
    conn: pika.BlockingConnection
    chan: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, host: str = ''):
        super().__init__()
        self.host = host

    def open(self, count: int):
        super().open(count)
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))  # Plan A,B
        self.chan = self.conn.channel()  # Plan A
        self.chan.basic_qos(prefetch_count=1)  # Plan A

    def close(self):
        self.chan.close()  # Plan A
        self.conn.close()  # Plan A,B


# == Async ==
class _RAQ(AQ):
    """RabbitMQ Async Queue.
    [RTFM](https://github.com/mosquito/aiormq))
    """

    def __init__(self, master: 'RAQC', __id: int):
        super().__init__(master, __id)

    async def open(self):
        ...

    def count(self) -> int:
        ...

    async def put(self, data: bytes):
        ...

    async def get(self, wait: bool = True) -> Optional[bytes]:
        ...

    async def get_all(self):
        ...

    async def close(self):
        ...


class RAQC(AQC):
    """RabbitMQ Async Queue Container."""
    _child_cls = _RAQ
