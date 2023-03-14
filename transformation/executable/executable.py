class Executable(object):

    def __init__(self, method, diff, filepath, task):
        self._method = method
        self._diff = diff
        self._filepath = filepath
        self._task = task

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = method

    @property
    def diff(self):
        return self._diff

    @diff.setter
    def diff(self, diff):
        self._diff = diff

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, filepath):
        self._filepath = filepath

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

    def execute(self):
        self._method(self._diff, self._filepath)


