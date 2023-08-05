# coding=utf-8
"""
Custom handler class
"""
import logging


class QueuedLoggingHandler(logging.Handler):
    """
    Redirects all log records in a queue for later processing
    """

    def __init__(self, queue):
        logging.Handler.__init__(self, level=logging.DEBUG)
        self.queue = queue

    def emit(self, record):
        """
        Places the log record into the queue
        """
        self.queue.put(record)
