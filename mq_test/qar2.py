"""Queue Async RabbitMQ #2.
Powered by [aio-pika](https://github.com/mosquito/aio-pika)
"""
# 1. std
from typing import Optional
# 2. 3rd
import aio_pika
import aio_pika.abc
# 3. local
from q import QA, QAc
# x. const
GET_TIMEOUT = 1


class _QAR2(QA):
    """RabbitMQ Async Queue."""
    _master: 'QAR2c'  # to avoid editor inspection warning
    chan: aio_pika.abc.AbstractChannel
    __q_name: str
    __q: aio_pika.abc.AbstractQueue

    def __init__(self, master: 'QAR2c', __id: int):
        super().__init__(master, __id)
        self.__q_name = f"{__id:04d}"

    async def open(self):
        self.chan = self._master.chan
        self.__q = await self.chan.get_queue(self.__q_name)

    async def count(self) -> int:
        q = await self.chan.get_queue(self.__q_name)
        return q.declaration_result.message_count

    async def put(self, data: bytes):
        await self.chan.default_exchange.publish(
            aio_pika.Message(body=data, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=self.__q_name
        )

    async def get(self, wait: bool = True) -> Optional[bytes]:
        # aio_pika.abc.AbstractIncomingMessage
        if im := await self.__q.get(no_ack=True, fail=False, timeout=1):
            return im.body

    async def get_all(self):
        while await self.get():
            ...

    async def get_all_freeze(self):
        async with self.__q.iterator() as q_iter:
            # FIXME: Cancel consuming after __aexit__
            async for msg in q_iter:
                async with msg.process():
                    print(f"Msg of {self.__q_name}")

    async def close(self):
        ...


class QAR2c(QAc):
    """RabbitMQ Async Queue Container."""
    title: str = "Queue Async (RabbitMQ (aio-pika))"
    _child_cls = _QAR2
    host: str
    conn: aio_pika.abc.AbstractConnection
    chan: aio_pika.abc.AbstractChannel

    def __init__(self, host: str = 'amqp://localhost'):
        super().__init__()
        self.host = host

    async def open(self, count: int):
        await super().open(count)
        self.conn = await aio_pika.connect(self.host)
        self.chan = await self.conn.channel()
        await self.chan.set_qos(prefetch_count=1)

    async def close(self):
        await self.chan.close()
        await self.conn.close()
