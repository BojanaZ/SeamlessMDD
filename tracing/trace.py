class Trace(object):

    def __init__(self, old_path=None, new_path=None):
        self._old_path = old_path
        self._new_path = new_path

    @property
    def old_path(self):
        return self._old_path

    @old_path.setter
    def old_path(self, path):
        self._old_path = path

    @property
    def new_path(self):
        return self._new_path

    @new_path.setter
    def new_path(self, path):
        self._new_path = path
