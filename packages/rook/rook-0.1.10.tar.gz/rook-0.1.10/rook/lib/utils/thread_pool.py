from concurrent.futures.thread import ThreadPoolExecutor

from lib.logger import logger


class LimitedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers, max_items):
        super(LimitedThreadPoolExecutor, self).__init__(max_workers)
        self._max_items = max_items

    def submit(self, fn, *args, **kwargs):
        if self._work_queue.qsize() >= self._max_items:
            logger.warning("Discarding processing item")
            return

        return super(LimitedThreadPoolExecutor, self).submit(fn, *args, **kwargs)
