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
# from . import ...  # not works for main.py
from const import Q_COUNT, W_COUNT, MSG_COUNT, R_COUNT, MSG
from q import QSc, QS, QAc
from qsm import QSMC
from qsd1 import QSD1c
from qsd2 import QSD2c
from qsr import QSRc
from qar2 import ConnMode, QAR2c


def mem_used() -> int:
    """Memory used, MB"""
    return round(psutil.Process().memory_info().rss / (1 << 20))


# == Sync ==
def stest(sqc: QSc):
    """Sync."""
    sqc.open(Q_COUNT)
    t0 = time.time()
    # 0. create writers and readers
    w_list: List[QS] = [sqc.q(i % Q_COUNT) for i in range(W_COUNT)]  # - writers
    r_list: List[QS] = [sqc.q(i % Q_COUNT) for i in range(R_COUNT)]  # - readers
    print(f"1: m={mem_used()}, t={round(time.time() - t0, 2)}, Wrtrs: {len(w_list)}, Rdrs: {len(r_list)}")
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
        r.get_all()
        # for _ in r:
        #    ...
    # x. the end
    m_count = [sqc.q(i).count() for i in range(Q_COUNT)]
    s_count = sum(m_count)
    print(f"3: m={mem_used()}, t={round(time.time() - t0, 2)}, msgs={s_count}")
    if s_count:
        print(f"Msgs: {m_count}")
    sqc.close()


# == async ==
async def atest(aqc: QAc, a_bulk=True):
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
    print(f"1: m={mem_used()}, t={round(time.time() - t0, 2)}, Wrtrs: {len(w_list)}, Rdrs: {len(r_list)}")
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
    stest(QSMC())
    stest(QSD1c())
    stest(QSD2c())
    stest(QSRc())


def amain():
    """Async entry point."""
    async def __inner():
        # await atest(QAMc())
        # await atest(QAR2c(mode=ConnMode.PlanA), False)
        # await atest(QAR2c(mode=ConnMode.PlanA), True)
        # await atest(QAR2c(mode=ConnMode.PlanB), False)
        # await atest(QAR2c(mode=ConnMode.PlanB), True)
        await atest(QAR2c(mode=ConnMode.PlanC), False)
        await atest(QAR2c(mode=ConnMode.PlanC), True)
    asyncio.run(__inner())


if __name__ == '__main__':
    # smain()
    amain()
