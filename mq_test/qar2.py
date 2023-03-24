"""
[RTFM](https://github.com/mosquito/aiormq))
"""
from enum import unique, IntEnum, auto
from typing import Optional

import aiormq

from q import QA, QAc


@unique
class ConnMode(IntEnum):
    PlanA = auto()  # 1 connection, 1 channel
    PlanB = auto()  # 1 connection, M channels (one per queue)
    PlanC = auto()  # M (connections + channel)


class _QAR2(QA):
    """RabbitMQ Async Queue."""
    _master: 'QAR2c'  # to avoid editor inspection warning
    conn: aiormq.connection.AbstractConnection
    chan: aiormq.channel.AbstractChannel
    __q: str

    def __init__(self, master: 'QAR2c', __id: int):
        super().__init__(master, __id)
        self.__q = f"{__id:04d}"

    async def open(self):
        if self._master.mode < ConnMode.PlanC:  # Plan A,B
            self.conn = self._master.conn
        else:  # Plan C
            self.conn = await aiormq.connect(self._master.host)
        if self._master.mode < ConnMode.PlanB:  # Plan A
            self.chan = self._master.chan
        else:  # Plan B,C
            self.chan = await self.conn.channel()
            await self.chan.basic_qos(prefetch_count=1)

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
        if self._master.mode > ConnMode.PlanA:
            await self.chan.close()  # Plan B,C
        if self._master.mode > ConnMode.PlanB:
            await self.conn.close()  # Plan C


class QAR2c(QAc):
    """RabbitMQ Async Queue Container."""
    title: str = "Queue Async (RabbitMQ (aiormq))"
    _child_cls = _QAR2
    host: str
    mode: ConnMode
    conn: aiormq.connection.Connection
    chan: aiormq.channel.Channel

    def __init__(self, host: str = 'amqp://localhost', mode: ConnMode = ConnMode.PlanA):
        super().__init__()
        self.host = host
        self.mode = mode

    async def open(self, count: int):
        await super().open(count)
        if self.mode < ConnMode.PlanC:
            self.conn = await aiormq.connect(self.host)  # Plan A,B
            if self.mode < ConnMode.PlanB:
                self.chan = await self.conn.channel()  # Plan A
                await self.chan.basic_qos(prefetch_count=1)  # Plan A

    async def close(self):
        if self.mode < ConnMode.PlanB:
            await self.chan.close()  # Plan A
        if self.mode < ConnMode.PlanC:
            await self.conn.close()  # Plan A,B
