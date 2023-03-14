from preview.preview import Preview


class ExecutableSet(object):

    def __init__(self, executable_set=None):
        if not executable_set:
            self._executable_set = []
        else:
            self._executable_set = executable_set

        self._preview = None

    @property
    def executable_set(self):
        return self._executable_set

    @executable_set.setter
    def executable_set(self, executable_set):
        self._executable_set = executable_set

    @property
    def preview(self):
        return self._preview

    @preview.setter
    def preview(self, preview):
        self._preview = preview

    def execute_set(self):
        if len(self._executable_set) == 0:
            return
        for executable in self._executable_set:
            executable.execute()
