"""Disk-based implementation."""
# 2. 3rd
import queuelib
import persistqueue
# 3. local
from bq import SQ, SQC


# == queuelib ==
class _D1SQ(SQ):
    """Disk-based #1 Sync Queue.
    1. [queuelib](https://github.com/scrapy/queuelib)
    """
    __q: queuelib.FifoDiskQueue

    def __init__(self, master: 'D1SQC', __id: int):
        super().__init__(master, __id)
        self.__q = queuelib.FifoDiskQueue(f"_d1sd/{__id:04d}")

    def open(self):
        ...

    def count(self) -> int:
        return len(self.__q)

    def put(self, data: bytes):
        return self.__q.push(data)

    def get(self, wait: bool = True) -> bytes:
        return self.__q.pop()

    def close(self):
        self.__q.close()


class D1SQC(SQC):
    """Disk-based #1 Sync Queue Container."""
    _child_cls = _D1SQ


# == persistqueue ==
class _D2SQ(SQ):
    """Disk-based #2 Sync Queue.
    2. [persistqueue](https://github.com/peter-wangxu/persist-queue)
    """
    __q: persistqueue.Queue

    def __init__(self, master: 'D2SQC', __id: int):
        super().__init__(master, __id)
        self.__q = persistqueue.Queue(f"_d2sd/{__id:04d}", autosave=True)  # FIXME: use .task_done()

    def open(self):
        ...

    def count(self) -> int:
        return self.__q.qsize()

    def put(self, data: bytes):
        return self.__q.put(data)

    def get(self, wait: bool = True) -> bytes:
        return self.__q.get(wait)

    def close(self):
        ...


class D2SQC(SQC):
    """Disk-based #2 Sync Queue Container."""
    _child_cls = _D2SQ
