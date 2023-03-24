# MQ

no | B | M | D | R
---|:-:|:-:|:-:|:-:
S  | + | + | 2 | +
A  | + | + | . | 2

- [ ] RxQ:
  - [ ] sure put (mandatory, confirm)
  - [ ] get ack (no_ack, ...)
  - [ ] chk connection * reconnect on demand
  - [ ] local/remote

## Future
- [ ] automation:
  - [ ] iterator (`__iter__`/`__next__`)
  - [ ] context (`__enter__`/`__exit__`)
- [ ] Try [rabbitpy](https://github.com/gmr/rabbitpy):
      ~~rpm~~ sleep since 04-2020

## RQ test

(1000w @ 100q * 10m = 100q x 100m = 10Km total)

- sync: 1.5..5"
- async:

Mod | O2O   | O2M   | M2M
----|------:|------:|------:
blk |  6…14 |  9…12 | *exc*
seq | 41…50 | 43…45 | 45…60

&hellip;

## Explore:
- DxMQ:
  + [queuelib](https://github.com/scrapy/queuelib):  
     Collection of persistent (disk-based) queues; 243 stars, 12 contribs, 3 releases (2021-08), 117 commits;
     &check;rpm
  + [persist-queue](https://github.com/peter-wangxu/persist-queue):  
     251 stars, 16 contribs, 17 releases (2017-07), 178 commits;
     &check;rpm
- RSMQ:
  + pika &check;rpm
- RAMQ:
  + [aio-pika](https://github.com/mosquito/aio-pika) ~~rpm~~
  + &rdsh;[aiormq](https://github.com/mosquito/aiormq) ~~rpm~~
  + &rdsh;[pamqp](https://github.com/gmr/pamqp) [*rpm*](https://koji.fedoraproject.org/koji/taskinfo?taskID=99061878)

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

## Dependencies:

gmr/pamqp -> gmr/aiorabbit
gmr/pamqp -> mosquito/aiormq -> mosquito/aio-pika
gmr/rabbitpy