from __future__ import print_function
import json
import re
import os
import numpy as np
from dplus.State import State, DomainPreferences
from dplus.FileReaders import SignalFileReader

class CalculationInput(object):
    def __init__(self, state):
        self._state = state
        self._use_gpu = False

    @property
    def use_gpu(self):
        return self._use_gpu

    @use_gpu.setter
    def use_gpu(self, flag):
        assert isinstance(flag, bool)
        self._use_gpu = flag

    @property
    def state(self):
        return self._state

    @property
    def x(self):
        return self._x

    @property
    def filenames(self):
        return self._state._get_all_filenames()

    def get_model(self, name_or_ptr):
        return self._state.get_model(name_or_ptr)

    def get_models_by_type(self, type):
        return self._state.get_models_by_type(type)

    def get_mutable_params(self):
        return self._state.get_mutable_params()

    def get_mutable_parameter_values(self):
        return self._state.get_mutable_parameter_values()

    def set_mutable_parameter_values(self, param_vals_array):
        self._state.set_mutable_parameter_values(param_vals_array)

    def export_all_parameters(self, filename):
        self._state.export_all_parameters(filename)


class GenerateInput(CalculationInput):
    def __init__(self, state):
        super().__init__(state)
        self._create_x_vector()

    @staticmethod
    def _web_load(args_dict):
        state = State()
        try:
            state.load_from_dictionary(args_dict["state"])
        except Exception as e:
            raise ValueError("Invalid state file")
        g = GenerateInput(state)
        g._x = args_dict["x"]
        return g

    @staticmethod
    def load_from_state_file(filename):
        with open(filename, 'r') as statefile:
            input = json.load(statefile)
        state = State()
        state.load_from_dictionary(input)
        g = GenerateInput(state)
        return g

    @staticmethod
    def _load_from_args_file(filename):
        with open(filename, 'r') as statefile:
            input = json.load(statefile)
        return GenerateInput._web_load(input["args"])

    @staticmethod
    def load_from_PDB(filename, qmax):
        # raise NotImplemented("Have not added support for PDB models")
        with open(filename) as pdbfile:  # checks file exists
            if not filename.endswith(".pdb"):
                raise NameError("Not a pdb file")
            grid_size = calculate_grid_size(pdbfile, qmax)
        from dplus.DataModels import Domain
        dom = Domain()
        dom.load_from_dictionary({
            "Geometry": "Domains",
            "ModelPtr": 1,
            "Populations": [{
                "ModelPtr": 2,
                "Models": [{
                    "AnomFilename": "",
                    "Centered": True,
                    "Constraints": [],
                    "ExtraConstraints": [{
                        "Link": -1,
                        "MaxIndex": -1,
                        "MaxValue": "inf",
                        "MinIndex": -1,
                        "MinValue": "-inf"
                    },
                        {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        },
                        {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        },
                        {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        },
                        {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        },
                        {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": 1,
                            "MinIndex": -1,
                            "MinValue": 0
                        },
                        {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": 1,
                            "MinIndex": -1,
                            "MinValue": 0
                        },
                        {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": 4,
                            "MinIndex": -1,
                            "MinValue": 0
                        }],
                    "ExtraMutables": [False,
                                      False,
                                      False,
                                      False,
                                      False,
                                      False,
                                      False,
                                      False],
                    "ExtraParameters": [
                        1,  # Scale
                        0,  # Solvent ED (333 if chosen)
                        0.05,  # Solvent Voxel size
                        0.14,  # Solvent radius
                        0,  # Outer solvent ED
                        0,  # Fill holes [0|1]
                        0,  # Solvent only [0|1]
                        0  # Solvent Method [0-4]
                        #		0 - No solvent
                        #		1 - Van der Waals
                        #		2 - Empirical
                        #		3 - Calculated
                        #		4 - Dummy Atoms
                    ],
                    "ExtraSigma": [0,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0],
                    "Filename": filename,  # TO BE INPUT BY USER
                    "Location": {
                        "alpha": 0,
                        "beta": 0,
                        "gamma": 0,
                        "x": 0,
                        "y": 0,
                        "z": 0
                    },
                    "LocationConstraints": {
                        "alpha": {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        },
                        "beta": {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        },
                        "gamma": {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        },
                        "x": {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        },
                        "y": {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        },
                        "z": {
                            "Link": -1,
                            "MaxIndex": -1,
                            "MaxValue": "inf",
                            "MinIndex": -1,
                            "MinValue": "-inf"
                        }
                    },
                    "LocationMutables": {
                        "alpha": False,
                        "beta": False,
                        "gamma": False,
                        "x": False,
                        "y": False,
                        "z": False
                    },
                    "LocationSigma": {
                        "alpha": 0,
                        "beta": 0,
                        "gamma": 0,
                        "x": 0,
                        "y": 0,
                        "z": 0
                    },
                    "ModelPtr": 3,
                    "Mutables": [],
                    "Name": "",
                    "Parameters": [],
                    "Sigma": [],
                    "Type": "PDB",
                    "Use_Grid": True,
                    "nExtraParams": 8,
                    "nLayers": 0,
                    "nlp": 0
                }],
                "PopulationSize": 1,
                "PopulationSizeMut": False
            }],
            "Scale": 1,
            "ScaleMut": False
        }
        )

        dom_pref = DomainPreferences()
        dom_pref.load_from_dictionary({
            "SignalFile": "",
            "Convergence": 0.001,  # An OK default
            "GridSize": grid_size,  # TO BE COMPUTED AT RUNTIME
            "OrientationIterations": 1000000,  # An OK default
            "OrientationMethod": "Monte Carlo (Mersenne Twister)",
            "UseGrid": True,
            "qMax": qmax  # TO BE INPUT BY USER
        })

        s = State()
        s.Domain = dom
        s.DomainPreferences = dom_pref
        return GenerateInput(s)

    @property
    def args(self):
        args = dict(args=dict(state=self._state.serialize(), x=self._create_x_vector()), options=dict(useGPU=self.use_gpu))
        return args

    def _create_x_vector(self):

        try:  # TODO: this is not good
            self._state.DomainPreferences.signal_file
            pass
        except:
            pass

        try:
            qmax = float(self._state.DomainPreferences.q_max)
        except KeyError:
            qmax = 7.5267

        try:
            qmin = float(self._state.DomainPreferences.q_min)
        except KeyError:
            qmin = 0

            #    try:
            #        resSteps =  float(self._state.DomainPreferences.generated_points)
            #    except KeyError:
        generatedPoints = self._state.DomainPreferences.generated_points
        generatedPoints += 1
        qvec = []
        for i in range(generatedPoints):
            val = qmin + (((qmax - qmin) * float(i))/ (generatedPoints - 1))
            qvec.append(val)
        self._x = qvec
        return qvec


class FitInput(CalculationInput):
    def __init__(self, state, graph=None, x=None, y=None):
        super().__init__(state)
        if x and y:
            self._x = x
            self._y = y
        elif graph:
            items = list(graph.items())
            items.sort(key=lambda item: item[0])
            self._x = [item[0] for item in items][:]
            self._y = [item[1] for item in items][:]
        else:
            raise ValueError("Either graph or x and y must be specified")
        self._mask = self._mask_vector()

    @property
    def args(self):
        return dict(args=dict(state=self._state.serialize(), x=self._x, y=self._y, mask=self._mask), options=dict(useGPU=self.use_gpu))

    @property
    def y(self):
        return self._y

    @staticmethod
    def _web_load(args_dict):
        state = State()
        state.load_from_dictionary(args_dict["state"])
        g = FitInput(state, x=args_dict["x"], y=args_dict["y"])
        g._mask = args_dict["mask"]  # possibly irrelevant
        return g

    @staticmethod
    def load_from_state_file(filename):
        with open(filename, 'r') as statefile:
            input = statefile.read()

        state = State()
        state.load_from_dictionary(json.loads(input))
        filename = state.DomainPreferences.signal_file
        x, y = load_x_and_y_from_file(filename)

        return FitInput(state, x=x, y=y)

    @staticmethod
    def _load_from_args_file(filename):
        with open(filename, 'r') as statefile:
            input = statefile.read()
        dict = json.loads(input)
        state = State()
        state.load_from_dictionary(dict["args"]["state"])

        filename = state.DomainPreferences.signal_file
        x, y = load_x_and_y_from_file(filename)
        return FitInput(state, x=x, y=y)

    def _mask_vector(self):
        # as of right now, the c++ code only has nomask, which is an array of zeros
        return [0] * len(self._x)

    def combine_results(self, fit_results):
        # Combine results returned from a Fit calculation
        def combine_model_parameters(parameters):
            # Combine parameters of just one model
            model_ptr = parameters['ModelPtr']
            model = self.get_model(model_ptr)
            mutables = model.get_mutable_params() or []
            updated = 0
            for param in parameters['Parameters']:
                if param['isMutable']:
                    if updated >= len(mutables):
                        raise ValueError("Found more 'isMutable' params in ParameterTree than in our state")
                    mutables[updated].value = param['Value']
                    updated += 1
            if updated != len(mutables):
                raise ValueError(
                    "Found a mismatch between number of 'isMutable' params in the ParamterTree and in our state")

        def recursive(parameters):
            combine_model_parameters(parameters)
            for sub in parameters['Submodels']:
                recursive(sub)

        recursive(fit_results._parameter_tree)


def _get_x_y_z_window(file):
    x_coords = []
    y_coords = []
    z_coords = []
    for line in file:
        record_name = line[0:6]
        if record_name in ["ATOM  ", "HETATM"]:
            x_coords.append(float(line[30:38]))
            y_coords.append(float(line[38:46]))
            z_coords.append(float(line[46:54]))
    x_len = max(x_coords) - min(x_coords)
    y_len = max(y_coords) - min(y_coords)
    z_len = max(z_coords) - min(z_coords)
    return x_len, y_len, z_len


def calculate_grid_size(pdbfile, q):
    import numpy as np
    x, y, z = _get_x_y_z_window(pdbfile)
    max_len = np.sqrt(x * x + y * y + z * z)
    max_len /= 10  # convert from nm to angstrom
    density = int(max_len) / np.pi
    grid_size = int(2 * q * density + 3)
    grid_size /= 10
    grid_size += 1
    grid_size = int(grid_size)
    grid_size *= 10
    if grid_size < 20:
        grid_size = 20  # minimum grid size
    return grid_size


def load_x_and_y_from_file(signal_filename):
        s = SignalFileReader(signal_filename)
        return s.x_vec, s.y_vec


'''
    textBoxGridSize->Text = Double(grid_size).ToString();

    /*
    actualGridSize = gridSize / 2 + Extras;

    long long i = actualGridSize;
    totalsz = (phiDivisions * i * (i + 1) * (3 + thetaDivisions + 2 * thetaDivisions * i)) / 6;
    totalsz++;    // Add the origin
    totalsz *= 2;    // Complex
    */

    long long i = (grid_size / 2) + 3;
    long long totalSize = (6 * i * (i + 1) * (3 + 3 + 2 * 6 * i)) / 6;
    totalSize++;
    totalSize *= 2;

    long long numBytes = sizeof(double) * totalSize;

    double mbs = double(numBytes) / (1024.*1024.);

    textBoxMemReq->Text = Int32(mbs+0.5).ToString();

    textBoxMemReq->BackColor = System::Drawing::Color::LimeGreen;
    labelWarning->Text = "";

    if (mbs > 250.)
    {
        textBoxMemReq->BackColor = System::Drawing::Color::Yellow;
        labelWarning->Text = "Note: You may want to consider using the hybrid method.";
    }

    if (mbs > 1000.)
    {
        textBoxMemReq->BackColor = System::Drawing::Color::Red;
        labelWarning->Text = "Caution: You should consider using the hybrid method.";
    }
'''