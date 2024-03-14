from utilities.utilities import get_project_root
from tracing.trace import Trace
import json
import os


class Tracer(object):

    def __init__(self, project_path=None):
        self._element_traces = {}
        self._last_trace_id = 0
        if project_path is None:
            project_path = get_project_root()

        self._data_loading_path = os.path.join(project_path, 'storage')

    @staticmethod
    def new_trace_id(last_no=0):
        id_ = last_no
        while True:
            yield id_
            id_ += 1

    def generate_new_trace_id(self):
        trace_id = self.new_trace_id(self._last_trace_id)
        while True:
            id_ = next(trace_id)
            if id_ not in self._element_traces:
                return id_

    @property
    def element_traces(self):
        return self._element_traces

    @element_traces.setter
    def element_traces(self, traces):
        self._element_traces = traces

    @property
    def last_trace_id(self):
        return self._last_trace_id

    @last_trace_id.setter
    def last_trace_id(self, last_trace):
        self.last_trace_id = last_trace

    @property
    def data_loading_path(self):
        return self._data_loading_path

    @data_loading_path.setter
    def data_loading_path(self, data_loading_path):
        self._data_loading_path = data_loading_path

    def add_element_trace(self, element_id, generator_id, trace):
        if element_id not in self._element_traces:
            self._element_traces[element_id] = {}

        if generator_id not in self._element_traces[element_id]:
            self._element_traces[element_id][generator_id] = []

        trace.id = self.generate_new_trace_id()
        self._element_traces[element_id][generator_id].append(trace)

    def add_multiple_element_traces(self, element_id, generator_id, traces):
        if element_id not in self._element_traces:
            self._element_traces[element_id] = {}

        if generator_id not in self._element_traces[element_id]:
            self._element_traces[element_id][generator_id] = []

        for trace in traces:
            trace.id = self.generate_new_trace_id()
            self._element_traces[element_id][generator_id].append(trace)

    def has_traces(self, element_id, generator_id):
        if element_id in self._element_traces:
            if generator_id is not None and generator_id in self._element_traces[element_id]:
                return True

        return False

    def get_traces(self, element_id, generator_id):
        result = []
        if element_id in self._element_traces:
            if generator_id is not None and generator_id in self._element_traces[element_id]:
                result = self._element_traces[element_id][generator_id]

        return result

    def update_trace(self, element_id, generator_id, new_trace):
        if element_id in self._element_traces:
            if generator_id in self.element_traces[element_id]:
                for i in range(0, len(self._element_traces[element_id][generator_id])):
                    trace = self._element_traces[element_id][generator_id][i]
                    if trace.id == new_trace.id:
                        trace.new_path = new_trace.new_path
                        trace.old_path = new_trace.old_path

    def get_all_traces(self, element_id):
        if element_id in self._element_traces:
            return self._element_traces[element_id]
        else:
            return {}

    def remove_traces(self, element_id, generator_id):
        if element_id in self._element_traces:
            if generator_id in self._element_traces[element_id]:
                self._element_traces[element_id][generator_id] = []

    def remove_element(self, element_id):
        if element_id in self._element_traces:
            del self._element_traces[element_id]

    def to_json(self):
        return json.dumps(self, cls=TracerJSONEncoder, indent=4)

    def to_dict(self):
        return TracerJSONEncoder().default(self)

    def save_to_json(self, path=None):
        if path is None:
            path = os.path.join(self._data_loading_path, "tracer.json")

        content = self.to_dict()
        with open(path, "w") as file:
            file.write(content)

    def load_from_json(self, path=None):
        if path is None:
            path = os.path.join(self._data_loading_path, "tracer.json")

        try:
            with open(path, "r") as file:
                json_content = json.load(file)
                return self.from_json(json_content)
        except OSError:
            print("Unable to load tracer.")

    def from_json(self, content):

        if type(content) == str:
            content = json.loads(content)

        self.data_loading_path = content['_data_loading_path']
        table_by_element = content["element_traces"]

        found_element_ids = set()
        found_old_generator_ids = set()

        for element_id, generators in self.element_traces.items():
            element_found = False
            for json_element_id, json_generators in table_by_element.items():
                if element_id == int(json_element_id):
                    element_found = True
                    found_element_ids.add(element_id)
                    for generator_id, value in generators.items():
                        for json_generator_id, json_value in json_generators:
                            if generator_id == json_generator_id:
                                found_old_generator_ids.add(generator_id)
                                trace = Trace.from_json(value)
                                self.update_trace(element_id, generator_id, trace)
                                break
                        else:
                            self.remove_traces(element_id, generator_id)
                    break
            if not element_found:
                self.remove_element(element_id)

        for json_element_id, json_generators in table_by_element.items():
            for json_generator_id, json_value in json_generators:
                if json_generator_id not in found_old_generator_ids:
                    trace = Trace.from_json(json_value)
                    self.update_trace(int(json_element_id), json_generator_id, trace)
        return self


class TracerJSONEncoder(json.JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Tracer):

            table_by_element = {}

            for element_id, generators in object_.element_traces.items():
                table_by_element[element_id] = []
                for generator_id, value in generators.items():
                    table_by_element[element_id].append((generator_id, value.to_dict()))

            object_dict = {"element_traces": table_by_element, "_last_trace_id": object_.last_trace_id,
                           "_data_loading_path": object_.data_loading_path}
            return json.dumps(object_dict, default=lambda o: o.to_dict(), indent=4)
        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
