# MQ

no | B | M | D | R
---|:-:|:-:|:-:|:-:
S  | + | + | 2 | +
A  | + | + | . | +

## TODO:
- RAQ: sure put
- RAQ: ack get
- `get_msgs()` iterator (<=.task_done())

## RQ test

(1000w @ 100q * 10msg = 10kmsg total):
- sync: 15..56"
- async (1 conn/1 chan): &hellip;
- async (1 conn/W chan): &hellip;
- async (W conn/1 chan): &hellip;


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
  + &rdsh;[pamqp](https://github.com/gmr/pamqp) ~~rpm~~

## Results
- Q_COUNT = 100
- W_COUNT = 1000
- R_COUNT = Q_COUNT
- MSG_COUNT = 1000
- Summary: 1000 writers @ 100 queues = 10 w/q x 1000 msgs == 100 queues x 10k msgs = 1M msgs
- macOS

- Sync:
  + M: 0.3..0.5"
  + D1: 9..15" (queuelib)
  + D2: 18'30..44'20" (persistqueue)
  + R: 9'..&hellip;  (pika, localhost)

- Async:
  + M: 1.5..2.2"
  + 