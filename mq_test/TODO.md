# MQ.ToDo

- [ ] RxQ:
  + [ ] sure put (mandatory, confirm), get (ack):
     - [x] `qsr1`: put(confirm, mandatory), get(auto_ack)
     - [x] `qar1`: put(confirm(?), mandatory), get(auto_ack)
     - [ ] `qar2`: 
  + [ ] chk connection * reconnect on demand
  + [ ] local/remote

## Future
- [ ] automation:
  - [ ] iterator (`__iter__`/`__next__`)
  - [ ] context (`__enter__`/`__exit__`)
- [ ] QADx

## RQ test

(1000w @ 100q * 10m = 100q x 100m = 10Km total)

- sync: 1.5..5"
- async:

Mod | O2O   | O2M   | M2M
----|------:|------:|------:
blk |  6…14 |  9…12 | *exc*
seq | 41…50 | 43…45 | 45…60

## Results
- `Q_COUNT` = 100
- `W_COUNT` = 1000
- `R_COUNT` = Q_COUNT
- `MSG_COUNT` = 1000
- Summary: 1000 writers @ 100 queues = 10 w/q x 1000 msgs == 100 queues x 10k msgs = 1M msgs
- macOS

- Sync:
  + M: 0.3..0.5"
  + D1: 9..15" (queuelib)
  + D2: 18'30..44'20" (persistqueue)
  + R: 3'7"..13'25"  (pika, localhost)

- Async:
  + M: 1.5..2.2" (bulk) / (seq)
  + R: 15'..34' (bulk)

## Notes:

gmr/pamqp -> {gmr/rabbitpy,gmr/aiorabbit}
gmr/pamqp -> mosquito/aiormq -> mosquito/aio-pika
