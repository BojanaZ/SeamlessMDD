
class Task(object):

    def __init__(self, function, priority, *args):
        self._task = function
        self._priority = priority
        self._args = args

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, priority):
        self._priority = priority

    def invoke(self):
        self._task(*self._args)

