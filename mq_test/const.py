Q_COUNT = 10  # prod: 100
W_COUNT = 10  # prod: 1000
MSG_COUNT = 10  # prod: 1000
R_COUNT = Q_COUNT
MSG_LEN = 128
MSG = b'\x00' * MSG_LEN
# prod: 1000 writers @ 100 queues = 10 w/q x 1000 msgs == 100 queues x 10k msgs = 1M msgs
# rq: 1000w @ 100q = 10 w/q x 10 msgs - 100q x 100 msg = 10k msgs
