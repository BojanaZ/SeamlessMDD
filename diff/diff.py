from diff.operation_type import OperationType


class Diff(object):

    def __init__(self, property_name, old_value, new_value, object_ref, operation_type=OperationType.UNKNOWN):
        self._operation_type = operation_type
        self._property_name = property_name
        self._old_value = old_value
        self._new_value = new_value
        self._object_ref = object_ref

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
    def object_ref(self):
        return self._object_ref

    @object_ref.setter
    def object_ref(self, object_ref):
        self._object_ref = object_ref

    def __eq__(self, other):
        if self._object_ref == other.object_ref and \
                self._new_value == other.new_value and \
                self._old_value == other.old_value and \
                self._operation_type == other.operation_type and \
                self._property_name == other.property_name:
            return True

        return False

    def __str__(self):
        if hasattr(self._old_value, "id"):
            old = self._old_value.id
        else:
            old = str(self._old_value)

        if hasattr(self._new_value, "id"):
            new = self._new_value.id
        else:
            new = str(self._new_value)

        return "{} {} {}: {} -> {}".format(self._object_ref, self._operation_type, self._property_name, old, new)
