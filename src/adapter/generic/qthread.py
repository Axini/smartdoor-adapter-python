import logging

from queue import Queue
from threading import Thread

class QThread:
    """
    Class that manages a thread which processes items in a queue.
    Items can be added to the queue, and the queue can be emptied.
    """

    def __init__(self, process_item):
        """
        Constructor.
        Args:
            process_item(item): method which is called for an item
                                retrieved from the queue by the _worker
        """
        self.process_item = process_item
        self.queue = Queue()
        self.thread = Thread(target = self._worker)

    def start(self):
        self.thread.start()

    def put(self, item):
        logging.debug('Adding item to the queue ({id})'.format(id=id(item)))
        self.queue.put(item)

    def clear_queue(self):
        while not self.queue.empty():
            item = self.queue.get()
            logging.debug('Removing item from queue ({id})'.format(id=id(item)))
            self.queue.task_done()

    def _worker(self):
        while True:
            item = self.queue.get()
            logging.debug('Processing item from queue ({id})'.format(id=id(item)))
            self.process_item(item)
            self.queue.task_done()
