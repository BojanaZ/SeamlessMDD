class TypedMixin(object):

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type_):
        self._type = type_

    def __lt__(self, other):
        return self._type < other.type

    def __le__(self, other):
        return self._type <= other.type

    def __gt__(self, other):
        return self._type > other.type

    def __ge__(self, other):
        return self._type >= other.type