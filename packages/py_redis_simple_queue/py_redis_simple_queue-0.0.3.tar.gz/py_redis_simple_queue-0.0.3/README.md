# Redis simple queue


Very simple implementation from article : http://peter-hoffmann.com/2012/python-simple-queue-redis-queue.html


## usage

```shell
    pip install py_redis_simple_queue
```

### The sender
```python
from redis import Redis

from redis_simple_queue import RedisQueue


connection = Redis() # see docs at https://docs.objectrocket.com/redis_python_examples.html


queue = RedisQueue('my_queue', connection)
queue.put('my message')
```

### The worker

```python
from redis import Redis

from redis_simple_queue import Worker, RedisQueue

class MyWorker(Worker):

    def run(self, msg):
        print(msg)
        # do something with message

connection = Redis()
queue = RedisQueue('my_queue', connection)
worker = MyWorker(queue)
worker.dequeue()
```
