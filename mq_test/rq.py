"""RabbitMQ implementation."""
# 1. std
from typing import Optional
# 2. 3rd
import pika
import aiormq
# 3. local
from bq import SQ, SQC, AQ, AQC


# == Sync ==
class _RSQ(SQ):
    """RabbitMQ Sync Queue.
    [RTFM](https://pika.readthedocs.io/en/stable/index.html)
    """
    _master: 'RSQC'  # to avoid editor inspection warning
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
    _master: 'RAQC'  # to avoid editor inspection warning
    chan: aiormq.channel.Channel
    __q: str

    def __init__(self, master: 'RAQC', __id: int):
        super().__init__(master, __id)
        self.__q = f"{__id:04d}"

    async def open(self):
        self.chan = self._master.chan  # Plan A

    async def count(self) -> int:
        ret = await self.chan.queue_declare(queue=self.__q, passive=True)
        return ret.message_count if ret else 0  # FIXME: hack

    async def put(self, data: bytes):
        await self.chan.basic_publish(
            exchange='',
            routing_key=self.__q,
            properties=aiormq.spec.Basic.Properties(delivery_mode=2),  # 2=persistent
            body=data
        )

    async def get(self, wait: bool = True) -> Optional[bytes]:
        #  no_ack (==pika.auto_ack): not require ack
        # method_frame, header_frame, body = await self.chan.basic_get(self.__q, no_ack=True)
        rsp = await self.chan.basic_get(self.__q, no_ack=True)
        if rsp:
            return rsp.body

    async def get_all(self):
        ret = True
        while ret:
            ret = await self.get(False)

    async def close(self):
        ...


class RAQC(AQC):
    """RabbitMQ Async Queue Container."""
    _child_cls = _RAQ
    host: str
    conn: aiormq.connection.Connection
    chan: aiormq.channel.Channel

    def __init__(self, host: str = 'amqp://localhost'):
        super().__init__()
        self.host = host

    async def open(self, count: int):
        await super().open(count)
        self.conn = await aiormq.connect(self.host)  # Plan A,B
        self.chan = await self.conn.channel()  # Plan A
        await self.chan.basic_qos(prefetch_count=1)  # Plan A

    async def close(self):
        await self.chan.close()  # Plan A
        await self.conn.close()  # Plan A,B
