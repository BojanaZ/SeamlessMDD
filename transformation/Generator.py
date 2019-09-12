
class Generator(object):

    def __init__(self):
        self._tasks = []

    @property
    def tasks(self):
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        self._tasks = tasks

