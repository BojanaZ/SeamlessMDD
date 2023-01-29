class Tracer(object):

    def __init__(self):
        self._element_traces = {}

    def add_element_trace(self, element_id, generator_id, trace):
        if element_id not in self._element_traces:
            self._element_traces[element_id] = {}

        if generator_id not in self._element_traces[element_id]:
            self._element_traces[element_id][generator_id] = []

        self._element_traces[element_id][generator_id].append(trace)

    def add_multiple_element_traces(self, element_id, generator_id, traces):
        if element_id not in self._element_traces:
            self._element_traces[element_id] = {}

        if generator_id not in self._element_traces[element_id]:
            self._element_traces[element_id][generator_id] = []

        for trace in traces:
            self._element_traces[element_id][generator_id].append(trace)

    def get_traces(self, element_id, generator_id):
        result = []
        if element_id in self._element_traces:
            if generator_id is not None and generator_id in self._element_traces[element_id]:
                result = self._element_traces[element_id][generator_id]

        return result

    def get_all_traces(self, element_id):
        if element_id in self._element_traces:
            return self._element_traces[element_id]
        else:
            return {}







