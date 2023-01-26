from diff.operation_type import OperationType


class Diff(object):

    def __init__(self, property_name, old_value, new_value, old_type, new_type, old_object_ref, new_object_ref,
                 operation_type=OperationType.UNKNOWN, prefix='', key=''):
        self._operation_type = operation_type
        self._property_name = property_name
        self._old_value = old_value
        self._new_value = new_value
        self._old_type = old_type
        self._new_type = new_type
        self._old_object_ref = old_object_ref
        self._new_object_ref = new_object_ref
        self._prefix = prefix
        self._key = key

    @property
    def operation_type(self):
        return self._operation_type

    @operation_type.setter
    def operation_type(self, type):
        self._operation_type = type

    @property
    def property_name(self):
        return self._property_name

    @property_name.setter
    def property_name(self, name):
        self._property_name = name

    @property
    def old_value(self):
        return self._old_value

    @old_value.setter
    def old_value(self, old):
        self._old_value = old

    @property
    def new_value(self):
        return self._new_value

    @new_value.setter
    def new_value(self, new):
        self._new_value = new

    @property
    def old_type(self):
        return self._old_type

    @old_type.setter
    def old_type(self, old):
        self._old_type = old

    @property
    def new_type(self):
        return self._new_type

    @new_type.setter
    def new_type(self, new):
        self._new_type = new

    @property
    def old_object_ref(self):
        return self._old_object_ref

    @old_object_ref.setter
    def old_object_ref(self, object_ref):
        self._old_object_ref = object_ref

    @property
    def new_object_ref(self):
        return self._new_object_ref

    @new_object_ref.setter
    def new_object_ref(self, object_ref):
        self._new_object_ref = object_ref

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        self._prefix = prefix

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    def __str__(self):
        if hasattr(self._old_value, "id"):
            old = self._old_value.id
        else:
            old = str(self._old_value)

        if hasattr(self._new_value, "id"):
            new = self._new_value.id
        else:
            new = str(self._new_value)

        return "{} {}: {} -> {}".format(self.operation_type, self._property_name, old, new)
