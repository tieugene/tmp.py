"""RabbitMQ implementation.
- Async:
  + [aio-pika](https://github.com/mosquito/aio-pika) ~~rpm~~
  + [aiormq](https://github.com/mosquito/aiormq) ~~rpm~~
"""
# 1. std
from typing import Optional
# 2. 3rd
import pika
# 3. local
from bq import SQ, SQC


# == Sync ==
class _RSQ(SQ):
    """RabbitMQ Sync Queue.
    [RTFM](https://pika.readthedocs.io/en/stable/index.html)
    """
    _master: 'RSQC'
    __q: str

    def __init__(self, master: 'RSQC', __id: int):
        super().__init__(master, __id)
        self.__q = f"{__id:04d}"
        # TODO: self.channel.queue_declare(queue=kju, passive=True) to chk queue exists

    def count(self) -> int:
        return self._master.ch.queue_declare(queue=self.__q, passive=True).method.message_count

    def put(self, data: bytes):
        self._master.ch.basic_publish(
            exchange='',
            routing_key=self.__q,
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
            body=data
        )

    def get(self, wait: bool = True) -> Optional[bytes]:  # FIXME: allwas no_wait
        method_frame, header_frame, body = self._master.ch.basic_get(self.__q, auto_ack=True)
        # or ... = channel.consume(kju): generator
        if method_frame:
            return body

    def close(self):
        ...


class RSQC(SQC):
    """Sync RabbitMQ Queue Container."""
    _child_cls = _RSQ
    __host: str
    __conn: pika.BlockingConnection
    ch: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, host: str = ''):
        super().__init__()
        self.__host = host

    def open(self, count: int):
        super().open(count)
        self.__conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.__host))
        self.ch = self.__conn.channel()
        self.ch.basic_qos(prefetch_count=1)

    def close(self):
        self.ch.close()
        self.__conn.close()
