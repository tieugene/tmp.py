"""RabbitMQ implementation.
- Sync:
  + pika &check;rpm
- Async:
  + [aio-pika](https://github.com/mosquito/aio-pika) ~~rpm~~
  + [aiormq](https://github.com/mosquito/aiormq) ~~rpm~~

"""
from typing import Optional

import pika

from . import bq


class RMQHelper:
    """RabbitMQ-powered (pika or async over)."""
    connection: pika.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, host: str):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        # TODO: self.channel.queue_declare(queue=kju, passive=True) to chk queue exists

    def __mk(self, name: str):
        m = self.channel.queue_declare(queue=name, durable=True)

    def tx(self, kju: str, msg: bytes):
        self.channel.basic_publish(
            exchange='',
            routing_key=kju,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                content_type='application/json'
            ),
            body=msg
        )

    def rx(self, kju: str):
        method_frame, header_frame, body = self.channel.basic_get(kju, auto_ack=True)
        # or ... = channel.consume(kju)
        if method_frame:
            print(body)

    def count(self, kju: str):
        return self.channel.queue_declare(queue=kju, passive=True).method.message_count


# == Sync ==
class _RSQ(bq.SQ):
    """RabbitMQ Sync Queue.
    [RTFM](https://pika.readthedocs.io/en/stable/index.html)
    """
    __q: queue.SimpleQueue

    def __init__(self, master: 'MRSQC', __id: int):
        super().__init__(master, __id)
        self.__q = queue.SimpleQueue()

    def count(self) -> int:
        """Get messages count."""
        return self.__q.qsize()

    def put(self, data: bytes):
        """Put a message."""
        return self.__q.put(data)

    def get(self, wait: bool = True) -> Optional[bytes]:
        """Get a message."""
        try:
            return self.__q.get(block=wait, timeout=None)
        except queue.Empty as e:
            return None

    def close(self):
        ...


class RSQC(bq.SQC):
    """Sync RabbitMQ Queue Container."""
    _child_cls = _RSQ
