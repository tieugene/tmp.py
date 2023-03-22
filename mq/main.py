#!/usr/bin/env python3
"""Message queue (MQ) tests.
- Sync/async
- RabbitMQ-/disk-/memory-based.
- K(10) queues × L(10..1000) writers × M(10) readers/writers × N(1...1000) messages (128 bytes)
"""
import time
from typing import List, Type

import psutil
from mmq import MSMQC
from mq.base import SMQ, SMQC

# x. const
Q_COUNT = 10
W_COUNT = 100
R_COUNT = Q_COUNT
MSG_COUNT = 1000
MSG_LEN = 128
mqc: SMQC


def mem_used() -> int:
    """Memory used, MB"""
    return round(psutil.Process().memory_info().rss / (1 << 20))


def stest(ccls: Type[SMQC]):
    """Sync."""
    global mqc
    print(f"0: m={mem_used()}")
    msg = b'\x00' * MSG_LEN
    mqc = ccls()
    mqc.init(Q_COUNT)
    t0 = time.time()
    # 0. create writers and readers
    # - writers
    w_list: List[SMQ] = []  # TODO: 1-line this
    for i in range(W_COUNT):
        w_list.append(mqc.q(i % Q_COUNT))
    # - readers
    r_list: List[SMQ] = []
    for i in range(R_COUNT):
        r_list.append(mqc.q(i % Q_COUNT))
    print(f"1: m={mem_used()}, t={round(time.time() - t0, 2)}")
    print(f"Queues: {Q_COUNT}, Writers: {len(w_list)}, Readers: {len(r_list)}")
    # 1. put
    for w in w_list:
        for _ in range(MSG_COUNT):
            w.put(msg)
    print(f"2: m={mem_used()}, t={round(time.time() - t0, 2)}")
    m_count = [mqc.q(i).count() for i in range(Q_COUNT)]
    print(f"Msgs: {m_count} ({sum(m_count)})")
    # 2. get
    for r in r_list:
        while r.count():
            r.get()
    # x. the end
    print(f"3: m={mem_used()}, t={round(time.time() - t0, 2)}")
    m_count = [mqc.q(i).count() for i in range(Q_COUNT)]
    print(f"Msgs: {m_count} ({sum(m_count)})")


def main():
    stest(MSMQC)


if __name__ == '__main__':
    main()
