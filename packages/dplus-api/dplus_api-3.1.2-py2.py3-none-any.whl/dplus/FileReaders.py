import json
import math
import numpy as np
from collections import OrderedDict


def _handle_infinity_for_json(obj):
    if isinstance(obj, float):
        if obj==math.inf:
            return("inf")
        if obj==-math.inf:
            return("-inf")
    elif isinstance(obj, dict):
        return dict((k, _handle_infinity_for_json(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        return [_handle_infinity_for_json(x) for x in obj]
    elif isinstance(obj, tuple):
        return map(_handle_infinity_for_json, obj)
    return obj

class NumpyHandlingEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyHandlingEncoder, self).default(obj)

class SignalFileReader:
    def __init__(self, filename):
        self.signal_filename=filename
        self._read()

    def _read(self):
        self.graph = OrderedDict()
        self.x_vec = []
        self.y_vec = []
        with open(self.signal_filename) as signal_file:
            for line in signal_file:
                if '#' in line:  # a header line
                    continue
                values = line.split()
                if len(values) > 1:  # two float values
                    try:
                        x = float(values[0])
                        y = float(values[1])
                        self.x_vec.append(x)
                        self.y_vec.append(y)
                        self.graph[float(x)] = float(y)
                    except ValueError:  # in the c++ code, if they werne't floats, it just continued
                        continue

