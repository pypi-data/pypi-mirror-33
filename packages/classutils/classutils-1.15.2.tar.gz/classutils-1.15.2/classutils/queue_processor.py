# encoding: utf-8

import logging_helper
from queue import Queue, Empty
from collections import Mapping
from .thread_pool import ThreadPoolMixIn

logging = logging_helper.setup_logging()


class QueueProcessor(ThreadPoolMixIn):

    def __init__(self,
                 *args,
                 **kwargs):

        super(QueueProcessor, self).__init__(*args,
                                             **kwargs)

        self._stop = True
        self.queue = Queue()

    def start_queue_processor(self):

        if self._stop:
            logging.debug(u'Starting Queue Processor...')

            # Set flag to allow loop activation
            self._stop = False

            # Open pool
            self.open_pool()

            # Run Main loop
            self._pool.submit_task(func=self._queue_processor_main_loop)

            logging.debug(u'Queue Processor Started')

        else:
            logging.debug(u'Queue Processor already started!')

    def stop_queue_processor(self):

        if not self._stop:
            logging.debug(u'Stopping Queue Processor, waiting for processes to complete...')

            # Signal loop termination
            self._stop = True

            # Wait for running processes to complete
            self.close_pool()

            logging.debug(u'Queue Processor Stopped')

    def _queue_processor_main_loop(self):

        while not self._stop:

            # Get next item from queue or wait for an item to be added.
            # Add 1 sec timeout so that it doesn't hang on exit.
            try:
                item = self.queue.get(timeout=1)

            except Empty:
                continue

            if isinstance(item, Mapping):
                # Pass item to worker thread
                self._pool.submit_task(func=self._queue_processor_worker,
                                       kwargs=item)

            else:
                logging.error(u'Item is not a Mapping, Discarding: {item}'.format(item=item))
                self.queue.task_done()

    def _queue_processor_worker(self,
                                **_):

        """ Run the kwarg set added to the queue.

        Ensure you call self.queue.task_done() when the function completes
        """

        self.queue.task_done()

    def __del__(self):
        self.stop_queue_processor()
