from metamodel.Element import Element

class Container(Element):

    def __init__(self, id):
        super().__init__(id)
        self._elements = []

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, elements):
        self.elements = elements