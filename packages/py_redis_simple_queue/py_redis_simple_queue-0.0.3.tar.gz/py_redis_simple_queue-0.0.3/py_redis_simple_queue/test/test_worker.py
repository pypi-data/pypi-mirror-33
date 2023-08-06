from unittest import TestCase
from mock import mock
from fakeredis import FakeRedis

from py_redis_simple_queue.worker import Worker
from py_redis_simple_queue.queue import RedisQueue

QUEUE_MODULE = 'py_redis_simple_queue.queue.'


class MyWorker(Worker):

    def __init__(self, redis_queue):
        super(MyWorker, self).__init__(redis_queue)
        self.messages = []

    def run(self, msg):
        # do something with message
        self.messages.append(msg)
        return msg


class TestWorker(TestCase):

    def setUp(self):
        self.redis_mock = mock.patch(QUEUE_MODULE + 'redis').start()
        self.redis_mock.redis.return_value = FakeRedis()
        self.queue = RedisQueue('test', FakeRedis())
        self.queue.put('test')
        self.queue.put('test')
        self.queue.get = mock.Mock()
        self.queue.get.side_effect = ['msg1', 'msg2', ValueError]
        self.worker = MyWorker(self.queue)

    def tearDown(self):
        self.redis_mock.stop()

    def testWorker(self):
        with self.assertRaises(ValueError):
            self.worker.dequeue()
        self.assertEqual(self.queue.get.call_count, 3)
        self.assertEqual(self.worker.messages, ['msg1', 'msg2'])
