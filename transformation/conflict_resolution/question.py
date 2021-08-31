
class Question(object):

    def __init__(self, id, title, text):
        self._id = id
        self._title = title
        self._text = text
        self._answers = []
        self._chosen_answer = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    @property
    def answers(self):
        return self._answers

    @answers.setter
    def answers(self, answers):
        self._answers = answers

    @property
    def chosen_answer(self):
        return self._chosen_answer

    @chosen_answer.setter
    def chosen_answer(self, chosen_answer):
        self._chosen_answer = chosen_answer