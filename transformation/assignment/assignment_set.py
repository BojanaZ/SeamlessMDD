class AssignmentSet(object):

    def __init__(self, *args):
        if not args:
            self._executable_set = []
        else:
            self._executable_set = list(args)

        self._context = None
        self._preview = None

    def setup_context(self, **kwargs):
        self._context = kwargs

    @property
    def executable_set(self):
        return self._executable_set

    @executable_set.setter
    def executable_set(self, executable_set):
        self._executable_set = executable_set

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    @property
    def preview(self):
        return self._preview

    @preview.setter
    def preview(self, preview):
        self._preview = preview

    def __len__(self):
        return len(self._executable_set)

    def execute_set(self):
        if len(self._executable_set) == 0:
            return
        for executable in self._executable_set:
            executable.execute(self._context)
