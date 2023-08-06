""" Writing data to IO text buffer using queue and working in separate
thread. Unfortunately, the current implementation depends on PyQt. """

from collections import deque
from threading import Lock, Event
from time import sleep
from PyQt5 import QtCore


class QueuedWriter:
    """ Tool for record data to text buffer using queue and
    thread. """
    def __init__(self, buff=None, thread_parent=None):
        self._buff = buff
        self._queue = deque([])
        self._lock = Lock()
        self._thread = RecordThread(
            context=self,
            parent=thread_parent
        )
        self._must_write = False
        self._convert_func = {
            'name': lambda x: x,
            'kwargs': {},
        }

    def set_buff(self, buff):
        """ Set IO buffer. """
        self._buff = buff

    def set_convert_func(self, func, **kwargs):
        """ Set function for convertion data sample to string. """
        self._convert_func = {
            'name': func,
            'kwargs': kwargs,
        }

    def save_queue(self):
        """ Move data from queue to buffer. """
        while len(self._queue) > 0:
            sample = self._queue.popleft()
            line = self._convert_func['name'](
                sample,
                **self._convert_func['kwargs'],
            )
            self._buff.write(line)

    def start_record(self):
        """ Start record. """
        self._thread.start()

    def stop_record(self):
        """ Stop record. """
        self._thread.stop()
        with self._lock:
            self._must_write = False

    def add_data(self, sample):
        """ Add data sample """
        self._queue.append(sample)


class RecordThread(QtCore.QThread):
    """ Thread in which samples recorded to IO buffer. """
    def __init__(self, context=None, parent=None):
        super().__init__(parent)
        self._lock = Lock()
        self._must_write = False
        self._can_quit = Event()
        self._context = context

    def run(self):
        """ Record data from queue to buffer. """
        self.setPriority(QtCore.QThread.LowestPriority)
        self._can_quit.clear()
        with self._lock:
            self._must_write = True
        while self._must_write:
            sleep(1)
            self._context.save_queue()
        self._context.save_queue()
        self._can_quit.set()

    def stop(self):
        """ Stop thread. """
        with self._lock:
            self._must_write = False
        self._can_quit.wait()
        self.quit()
