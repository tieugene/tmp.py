# MQ.ToDo

- [ ] RxQ:
  + [ ] chk connection * reconnect on demand
  + [ ] local/remote

## Future
- [ ] automation:
  - [ ] iterator (`__iter__`/`__next__`)
  - [ ] context (`__enter__`/`__exit__`)
- [ ] QADx

## RQ test

(1000w @ 100q * 10m = 100q x 100m = 10Kmsg total)

- sync: 1.5…5"
- async (bulk): 6…14" … 9…12"

## Results
- `Q_COUNT` = 100
- `W_COUNT` = 1000
- `R_COUNT` = Q_COUNT
- `MSG_COUNT` = 1000
- total = 1 Mmsg
- macOS

- Sync:
  + M: 0.3..0.5"
  + D1: 9..15" (queuelib)
  + D2: 18'30..44'20" (persistqueue)
  + R: 3'7"..13'25"  (pika, localhost)

- Async (bulk):
  + M: 1.5..2.2"
  + R: 15'..34'
