# Notes

## Dependencies:

gmr/pamqp -> {gmr/rabbitpy,gmr/aiorabbit}
gmr/pamqp -> mosquito/aiormq -> mosquito/aio-pika

## QARx tests:

- 1 conn/1 chan == 1 conn/N chan == N conn/N chan (but last can fail)
- sequenced slower than bulk for 3..4 times
