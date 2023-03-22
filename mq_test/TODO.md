# MQ

- [ ] Base:
  + [x] SQ
  + [ ] AQ
- [ ] M:
  + [x] [MSQ](https://docs.python.org/3/library/queue.html)
  + [ ] [MAQ](https://docs.python.org/3/library/asyncio-queue.html)
- [ ] D:
  + [ ] DSQ
  + [ ] DAQ
- [ ] R:
  + [ ] RSQ
  + [ ] RAQ

## Explore:
- DxMQ:
  + [queuelib](https://github.com/scrapy/queuelib):  
     Collection of persistent (disk-based) queues; 243 stars, 12 contribs, 3 releases (2021-08), 117 commits
  + [persist-queue](https://github.com/peter-wangxu/persist-queue):  
     251 stars, 16 contribs, 17 releases (2017-07), 178 commits
- RSMQ:
  + pika &check;rpm
- RAMQ:
  + [aio-pika](https://github.com/mosquito/aio-pika) ~~rpm~~
  + [aiormq](https://github.com/mosquito/aiormq) ~~rpm~~

## Results
- Q_COUNT = 100
- W_COUNT = 1000
- R_COUNT = Q_COUNT
- MSG_COUNT = 1000
- Summary: 1000 writers @ 100 queues = 10 w/q x 1000 msgs == 100 queues x 10k msgs = 1M msgs

- M: 0.5"
- D1: 9..15" (queuelib, macOS)
- 