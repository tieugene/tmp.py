#!/usr/bin/env python3
"""Message queue (MQ) tests.
- Sync/async
- RabbitMQ-/disk-/memory-based.
- K(10) queues × L(10..1000) writers × M(10) readers/writers × N(1...1000) messages (128 bytes)
"""
# 1. std
from typing import List, Tuple
import time
import asyncio
# 2. 3rd
import psutil
# 3. local
# from . import bq, mq, dq, rq  # not works for main.py
from bq import SQC, SQ, AQC
from mq import MSQC, MAQC
from dq import D1SQC, D2SQC
from rq import RSQC, RAQC, ConnMode
# x. const
Q_COUNT = 100  # prod: 100
W_COUNT = 1000  # prod: 1000
MSG_COUNT = 10  # prod: 1000
# prod: 1000 writers @ 100 queues = 10 w/q x 1000 msgs == 100 queues x 10k msgs = 1M msgs
# rq: 1000w @ 100q = 10 w/q x 10 msgs - 100q x 100 msg = 10k msgs
R_COUNT = Q_COUNT
MSG_LEN = 128
MSG = b'\x00' * MSG_LEN


def mem_used() -> int:
    """Memory used, MB"""
    return round(psutil.Process().memory_info().rss / (1 << 20))


# == Sync ==
def stest(sqc: SQC):
    """Sync."""
    sqc.open(Q_COUNT)
    t0 = time.time()
    # 0. create writers and readers
    w_list: List[SQ] = [sqc.q(i % Q_COUNT) for i in range(W_COUNT)]  # - writers
    r_list: List[SQ] = [sqc.q(i % Q_COUNT) for i in range(R_COUNT)]  # - readers
    print(f"1: m={mem_used()}, t={round(time.time() - t0, 2)}\nWriters: {len(w_list)}, Readers: {len(r_list)}")
    # 1. put
    for w in w_list:
        for _ in range(MSG_COUNT):
            w.put(MSG)
    m_count = [sqc.q(i).count() for i in range(Q_COUNT)]
    s_count = sum(m_count)
    print(f"2: m={mem_used()}, t={round(time.time() - t0, 2)}, msgs={s_count}")
    # if s_count:
    #    print("Msgs: {m_count}")
    # 2. get
    for r in r_list:
        while r.get(False):
            ...
    # x. the end
    m_count = [sqc.q(i).count() for i in range(Q_COUNT)]
    s_count = sum(m_count)
    print(f"2: m={mem_used()}, t={round(time.time() - t0, 2)}, msgs={s_count}")
    if s_count:
        print(f"Msgs: {m_count}")
    sqc.close()


# == async ==
async def atest(aqc: AQC, a_bulk=True):
    """Async."""
    async def __counters() -> Tuple[int]:
        __qs = await asyncio.gather(*[aqc.q(i) for i in range(Q_COUNT)])
        __count = await asyncio.gather(*[__q.count() for __q in __qs])
        return tuple(map(int, __count))
    await aqc.open(Q_COUNT)
    t0 = time.time()
    # 0. create writers and readers
    w_list = await asyncio.gather(*[aqc.q(i % Q_COUNT) for i in range(W_COUNT)])  # - writers
    r_list = await asyncio.gather(*[aqc.q(i % Q_COUNT) for i in range(R_COUNT)])  # - readers
    print(f"1: m={mem_used()}, t={round(time.time() - t0, 2)}, Wrtr: {len(w_list)}, Rdrs: {len(r_list)}")
    # 1. put (MSG_COUNT times all the writers)
    for _ in range(MSG_COUNT):
        if a_bulk:
            await asyncio.gather(*[w.put(MSG) for w in w_list])
        else:
            for w in w_list:
                await w.put(MSG)
    # RAW err
    m_count = await __counters()
    s_count = sum(m_count)
    print(f"2: m={mem_used()}, t={round(time.time() - t0, 2)}, msgs={s_count}")
    # 2. get
    await asyncio.gather(*[r.get_all() for r in r_list])
    # x. the end
    m_count = await __counters()
    s_count = sum(m_count)
    print(f"3: m={mem_used()}, t={round(time.time() - t0, 2)}, msgs={s_count}")
    if s_count:
        print(f"Msgs: {m_count}")
    await aqc.close()


# == entry points ==
def smain():
    """Sync."""
    # stest(MSQC())
    # stest(dq.D1SQC())
    # stest(dq.D2SQC())
    stest(RSQC())


def amain():
    """Async entry point."""
    async def __inner():
        # await atest(MAQC())
        # await atest(RAQC(mode=ConnMode.PlanA), False)
        # await atest(RAQC(mode=ConnMode.PlanA), True)
        # await atest(RAQC(mode=ConnMode.PlanB), False)
        # await atest(RAQC(mode=ConnMode.PlanB), True)
        await atest(RAQC(mode=ConnMode.PlanC), False)
        await atest(RAQC(mode=ConnMode.PlanC), True)
    asyncio.run(__inner())


if __name__ == '__main__':
    # smain()
    amain()
