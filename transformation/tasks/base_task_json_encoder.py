import json
from multigen.generator import Task


class BaseTaskJSONEncoder(json.JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Task):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if key not in ['environment', 'formatter']}

            object_dict['class'] = type(object_).__name__

            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
