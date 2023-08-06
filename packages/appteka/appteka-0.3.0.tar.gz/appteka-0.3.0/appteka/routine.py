""" This module implements the base class for routines. """

class Routine:
    """ Base routine class. """
    def __init__(self):
        self.progress_hook = lambda x : True
        self.finished_hook = lambda : True
        self.volume = 1
        self.ready = 0

    def add_progress(self, part):
        self.ready += part
        self.progress_hook(int(100*self.ready/self.volume))

    def __call__(self):
        raise NotImplementedError
