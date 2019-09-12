class Element(object):

    def __init__(self, id):
        self._id = id
        self._container = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def container(self):
        return self._container

    @container.setter
    def container(self, container):
        self._container = container
        
if __name__ == '__main__':
    el = Element(5)
    el.id = 7
    print(el.id)
