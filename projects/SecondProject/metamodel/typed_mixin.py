class TypedMixin(object):

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type_):
        self._type = type_
