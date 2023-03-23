#!/usr/bin/env python3
"""Message queue (MQ) tests.
- Sync/async
- RabbitMQ-/disk-/memory-based.
- K(10) queues × L(10..1000) writers × M(10) readers/writers × N(1...1000) messages (128 bytes)
"""
# 1. std
from typing import List, Type
import time
import asyncio
# 2. 3rd
import psutil
# 3. local
from . import bq, mq, dq

# x. const
Q_COUNT = 100
W_COUNT = 1000
R_COUNT = Q_COUNT
MSG_COUNT = 1000
MSG_LEN = 128
MSG = b'\x00' * MSG_LEN
# 1000 writers @ 100 queues = 10 w/q x 1000 msgs == 100 queues x 10k msgs = 1M msgs


def mem_used() -> int:
    """Memory used, MB"""
    return round(psutil.Process().memory_info().rss / (1 << 20))


# == Sync ==
def stest(ccls: Type[bq.SQC]):
    """Sync."""
    sqc: bq.SQC = ccls()
    sqc.open(Q_COUNT)
    t0 = time.time()
    # 0. create writers and readers
    w_list: List[bq.SQ] = [sqc.q(i % Q_COUNT) for i in range(W_COUNT)]  # - writers
    r_list: List[bq.SQ] = [sqc.q(i % Q_COUNT) for i in range(R_COUNT)]  # - readers
    print(f"1: m={mem_used()}, t={round(time.time() - t0, 2)}\nWriters: {len(w_list)}, Readers: {len(r_list)}")
    # 1. put
    for w in w_list:
        for _ in range(MSG_COUNT):
            w.put(MSG)
    m_count = [sqc.q(i).count() for i in range(Q_COUNT)]
    print(f"2: m={mem_used()}, t={round(time.time() - t0, 2)}\nMsgs: {m_count} ({sum(m_count)})")
    # 2. get
    for r in r_list:
        while r.get(False):
            ...
    # x. the end
    sqc.close()
    m_count = [sqc.q(i).count() for i in range(Q_COUNT)]
    print(f"3: m={mem_used()}, t={round(time.time() - t0, 2)}\nMsgs: {m_count} ({sum(m_count)})")


def main():
    stest(mq.MSQC)
    # stest(dq.D1SQC)
    # stest(dq.D2SQC)


# == async ==
async def atest(ccls: Type[bq.AQC]):
    """Async."""
    aqc: bq.AQC = ccls()
    await aqc.open(Q_COUNT)
    t0 = time.time()
    # 0. create writers and readers
    w_list = await asyncio.gather(*[aqc.q(i % Q_COUNT) for i in range(W_COUNT)])  # - writers
    r_list = await asyncio.gather(*[aqc.q(i % Q_COUNT) for i in range(R_COUNT)])  # - readers
    print(f"1: m={mem_used()}, t={round(time.time() - t0, 2)}\nWriters: {len(w_list)}, Readers: {len(r_list)}")
    # 1. put
    funcs = [w.put(MSG) for w in w_list for _ in range(MSG_COUNT)]
    for f in funcs:  # ver.1: sequenced (fast)
        await f
    # await asyncio.gather(*funcs)  # ver.2: async (slow)
    m_count = [(await aqc.q(i)).count() for i in range(Q_COUNT)]
    print(f"2: m={mem_used()}, t={round(time.time() - t0, 2)}\nMsgs: {m_count} ({sum(m_count)})")
    # 2. get
    await asyncio.gather(*[r.get_all() for r in r_list])
    # x. the end
    await aqc.close()
    m_count = [(await aqc.q(i)).count() for i in range(Q_COUNT)]  # FIXME:
    print(f"3: m={mem_used()}, t={round(time.time() - t0, 2)}\nMsgs: {m_count} ({sum(m_count)})")


async def amain():
    await atest(mq.MAQC)
    ...


if __name__ == '__main__':
    main()
    asyncio.run(amain())
