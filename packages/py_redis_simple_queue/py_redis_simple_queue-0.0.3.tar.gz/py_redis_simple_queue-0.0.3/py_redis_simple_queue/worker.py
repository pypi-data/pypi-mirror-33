from abc import ABCMeta, abstractmethod
from redis import ConnectionError


class Worker(object):
    """ Another simple worker abstract class """
    __metaclass__ = ABCMeta

    def __init__(self, redis_queue):
        self.__queue = redis_queue

    def dequeue(self):
        """ Dequeue messages and put into run """
        while True:
            try:
                msg = self.__queue.get()
                self.run(msg)
            except ConnectionError:
                print('exiting... connection error')
                return

    @abstractmethod
    def run(self, msg):
        pass

