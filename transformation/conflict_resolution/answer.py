class Answer(object):

    def __init__(self, id, text, task = None):
        self._id = id
        self._text = text
        self._task = task

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task


