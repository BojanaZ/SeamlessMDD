from json import JSONEncoder
from multigen.generator import TemplateGenerator


class BaseGeneratorJSONEncoder(JSONEncoder):

    def default(self, object_):

        if isinstance(object_, TemplateGenerator):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if
                           key not in ['tasks', '__len__', '_tracer', 'parsers', "_parser_type"]}

            object_dict['class'] = type(object_).__name__

            if hasattr(object_, "tasks"):
                object_dict["tasks"] = []

                for task in object_.tasks:
                    task_dict = task.to_dict()
                    object_dict["tasks"].append(task_dict)

            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return JSONEncoder.default(self, object_)
