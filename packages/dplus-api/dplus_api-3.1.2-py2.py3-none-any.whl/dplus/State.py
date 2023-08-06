import json

from dplus.Amplitudes import Amplitude

__author__="Devora Witty"
'''
Represents a state file and the state's DomainPreferences and FittingPreferences. 
Domain is located in DataModels.py
'''

import warnings
from collections import OrderedDict
from dplus.FileReaders import SignalFileReader
from dplus.DataModels import Domain, Parameter


class DomainPreferences:
    def __init__(self):
        self.__signal_file = ""
        self.__convergence = 0.001
        self.__grid_size = 200
        self.__orientation_iterations = 100
        self.__orientation_method = "Monte Carlo (Mersenne Twister)"
        self.__use_grid = False
        self.__q_max = 7.5
        self.__q_min = 0
        self.__res_steps = 800        # self.DrawDistance = 50
        # self.LevelOfDetail = 3
        # self.Fitting_UpdateDomain = False
        # self.Fitting_UpdateGraph = True
        # self.UpdateInterval = 100

    @property
    def q_max(self):
        '''
         The maximal value in the q range. If SignalFile is not blank,
         qMax must equal the largest x-value in the SignalFile
        '''
        return self.__q_max

    @q_max.setter
    def q_max(self, x):
        if x <= 0:
            raise ValueError("q_max must be greater than zero")
        self.__q_max=x
        if self.signal_file:
            try:
                s=SignalFileReader(self.signal_file)
                graph = s.graph
                self.__q_max == graph.popitem()[0]  # last x value
                if x != self.__q_max:
                    warnings.warn(
                    "q_max must be equal to highest x value in signal file. q_max's value has not been changed")
            except FileNotFoundError:
                pass #TODO

    @property
    def q_min(self):
        '''
         The maximal value in the q range. If SignalFile is not blank,
         qMax must equal the largest x-value in the SignalFile
        '''
        return self.__q_min

    @q_min.setter
    def q_min(self, x):
        if x < 0:
            raise ValueError("q_min must be greater than zero")
        if x > self.q_max:
            raise ValueError("q_min must be smaller than q_max")
        self.__q_min=x
        if self.signal_file:
            try:
                s = SignalFileReader(self.signal_file)
                graph = s.graph

                self.__q_min == graph.popitem(last=False)[0]  # first x value
                if x != self.__q_min:
                    warnings.warn(
                    "q_min must be equal to lowest x value in signal file. q_min's value has not been changed")
            except FileNotFoundError:
                pass #TODO

    @property
    def signal_file(self):
        '''
        The path to the signal file. Must be present when fitting,
            optional when generating (Generate uses the x-values from
            this file)
        '''
        return self.__signal_file

    @signal_file.setter
    def signal_file(self, sigfile):
        self.__signal_file = sigfile #TODO: change later, right now they're all invalid
        return
        if not sigfile or sigfile == "":
            self.__signal_file = sigfile
            return
        try:
            s=SignalFileReader(self.signal_file)
            graph = s.graph
            self.__q_max == graph.popitem()[0]  # last x value
            self.__q_min == graph.popitem(last=False)[0]  # first x value
        except FileNotFoundError:
            raise ValueError("signalfile must be valid file (or blank, for generate")

    @property
    def convergence(self):
        '''
        convergence: A convergence criteria for the orientation average. Usually
                    	10e-3 or so. See manual, chapter 6.
        '''
        return self.__convergence

    @convergence.setter
    def convergence(self, convergence):
        try:
            self.__convergence = float(convergence)
        except:
            raise ValueError("convergence must be valid number")

    @property
    def grid_size(self):
        '''
        The size of the the grid to be used (or not if !UseGrid).
        Must be a positive even integer. Minimum size is 20.
        '''
        return self.__grid_size

    @grid_size.setter
    def grid_size(self, grid_size):
        try:
            self.__grid_size = int(grid_size)
        except:
            raise ValueError("Grid size must be an integer")
        if grid_size % 2 != 0:
            raise ValueError("Grid size must be even")
        if grid_size < 20:
            raise ValueError("Minimum grid size is 20")

    @property
    def orientation_method(self):
        '''
            ["Monte Carlo (Mersenne Twister)","Adaptive (VEGAS) Monte Carlo","Adaptive Gauss Kronrod"]
            See manual chapter 6. The first is the only one implemented
            on both CPU and GPU. Selecting VEGAS makes the amplitudes
            not be saved to files (they never leave the GPU), but is
            often much faster then vanilla Monte Carlo.
        '''
        return self.__orientation_method

    @orientation_method.setter
    def orientation_method(self, method):
        if method not in ["Monte Carlo (Mersenne Twister)",
                          "Adaptive (VEGAS) Monte Carlo",
                          "Adaptive Gauss Kronrod"]:
            raise ValueError(
                "Orientation method must be either: Monte Carlo (Mersenne Twister), Adaptive (VEGAS) Monte Carlo, or Adaptive Gauss Kronrod")
        self.__orientation_method = method

    @property
    def use_grid(self):
        '''
        boolean flag for using or not using grid
        '''
        return self.__use_grid

    @use_grid.setter
    def use_grid(self, use_grid):
        if type(use_grid) == bool:
            self.__use_grid = use_grid
        else:
            raise ValueError("use_grid must be a boolean")

    @property
    def orientation_iterations(self):
        '''
        The number of iterations (or depth in the case of Gauss
         Krondrod) to be used in the orientation average. A good
         default value is 1,000,000. See manual, chapter 6.
        '''
        return self.__orientation_iterations

    @orientation_iterations.setter
    def orientation_iterations(self, x):
        try:
            if x <= 0:
                raise ValueError("Orientation iterations must be greater than zero")
            self.__orientation_iterations = int(x)
        except:
            raise ValueError("Orientation iterations must be integer")

    @property
    def generated_points(self):
        '''
        The number of point to generate between qmin(0) to qmax
         default value is 800
        '''
        return self.__res_steps

    @generated_points.setter
    def generated_points(self, x):
        if x <= 0:
            raise ValueError("gen_res must be greater than zero")
        try:
            self.__res_steps=int(x)
        except:
            raise ValueError("generated points must be integer")

    def serialize(self):
        return {
            "SignalFile": self.signal_file,
            "Convergence": self.convergence,
            "GridSize": self.grid_size,
            "UseGrid": self.use_grid,  # [true,false] Self explanatory?
            "qMin": self.q_min,
            "qMax": self.q_max,
            "OrientationIterations": self.orientation_iterations,
            "OrientationMethod": self.orientation_method,

            #####irrelevant/defunct parameters:####
            "DrawDistance": 200,  # GUI parameter. Determines how far camera can "see." It's a
            #	cutoff for rendering.
            "LevelOfDetail": 1,  # GUI parameter. Determines the level of detail when rendering.
            "Fitting_UpdateDomain": False,  # Deprecated and disabled in the GUI. Default should be false?
            "Fitting_UpdateGraph": False,  # Deprecated and disabled in the GUI. Default should be false?
            "UpdateInterval": 100,  # The number of milliseconds that the frontend waits before
            "GeneratedPoints": self.generated_points, # The length of x vector
            #	polling the backend for progress. Broken.
        }

    def load_from_dictionary(self, json):
        try:
            self.signal_file = json["SignalFile"]
        except KeyError:
            self.signal_file=""
        self.convergence = json["Convergence"]
        self.grid_size = json["GridSize"]
        self.use_grid = json["UseGrid"]
        try:
            self.q_min = json["qMin"]
        except: # qMin doesn't exist in the json, so it default value is 0
            self.q_min = 0
        self.q_max = json["qMax"]
        self.orientation_iterations = json["OrientationIterations"]
        self.orientation_method = json["OrientationMethod"]
        if "GeneratedPoints" in json.keys():
            self.generated_points = json["GeneratedPoints"]
        else:
            self.generated_points = 800

    def __str__(self):
        return (str(self.serialize()))

class FittingPreferences:
    def __init__(self):
        self.__Convergence = 0.1
        self.__DerEps = 0.1
        self.__FittingIterations = 20
        self.__LossFuncPar1 = 0.5
        self.__LossFuncPar2 = 0.5
        self.__LossFunction = "Trivial Loss"
        self.__StepSize = 0.01
        self.__XRayResidualsType = "Normal Residuals"
        self.__DoglegType = "Traditional Dogleg"
        self.__LineSearchDirectionType = "L-BFGS"
        self.__LineSearchType = "Wolfe"
        self.__MinimizerType = "Trust Region"
        self.__NonlinearConjugateGradientType = "Fletcher Reeves"
        self.__TrustRegionStrategyType = "Levenberg-Marquardt"
    
    @property
    def loss_function(self):
        '''
        See http://ceres-solver.org/nnls_tutorial.html for explanation.
        acceptable values: "Trivial Loss","Huber Loss","Soft L One Loss","Cauchy Loss","Arctan Loss","Tolerant Loss"
        '''
        return self.__LossFunction

    @loss_function.setter
    def loss_function(self, loss_func):
        '''
        :param loss_func: acceptable values: "Trivial Loss","Huber Loss","Soft L One Loss","Cauchy Loss","Arctan Loss","Tolerant Loss"
           all loss functions except Trivial require one parameter (default 0.5)
        Tolerant loss requires a second parameter (will be ignored for all other types) (default 0.5)
        '''
        if loss_func not in ["Trivial Loss","Huber Loss","Soft L One Loss",
                             "Cauchy Loss","Arctan Loss","Tolerant Loss"]:
            raise ValueError("Loss function not valid. Please choose from:"
                             "Trivial, Huber, Soft L One, Cauchy, Arctan, or Tolerant Loss")

        self.__LossFunction=loss_func

    @property
    def loss_func_param_one(self):
        '''
        required for all loss functions but Trivial
        '''
        return self.__LossFuncPar1

    @loss_func_param_one.setter
    def loss_func_param_one(self, x):
        self.__LossFuncPar1=x

    @property
    def loss_func_param_two(self):
        '''
        required for Tolerant Loss function
        '''
        return self.__LossFuncPar2

    @loss_func_param_two.setter
    def loss_func_param_two(self, x):
        self.__LossFuncPar2 = x

    @property
    def convergence(self):
        '''
        # The convergence criteria passed on to Ceres that determines
        #	when the fitting process has converged.
        #	Required.
        '''
        return self.__Convergence

    @convergence.setter
    def convergence(self,x):
        if x>0:
            self.__Convergence=x
        else:
            raise ValueError("convergence must be positive")

    @property
    def x_ray_residuals_type(self):
        '''
        # ["Normal Residuals","Ratio Residuals","Log Residuals"]
            #	A function that determines how the residuals are treated.
            #	Apparently not documented anywhere. Corresponds to [XRayResiduals,
            #	XRayRatioResiduals,XRayLogResiduals] in modelfitting.cpp.
            #	Required.
        '''
        return self.__XRayResidualsType

    @x_ray_residuals_type.setter
    def x_ray_residuals_type(self, xtype):
        if xtype not in ["Normal Residuals","Ratio Residuals","Log Residuals"]:
            raise ValueError("x ray residual type must be Normal, Ratio, or Lod Residuals")
        self.__XRayResidualsType=xtype

    @property
    def fitting_iterations(self):
        '''
  # The number of iterations the fitter should use before stopping.
            #	Note that this is also the number of "inner iterations" that
            #	ceres uses (http://ceres-solver.org/nnls_solving.html#inner-iterations).
        '''
        return self.__FittingIterations

    @fitting_iterations.setter
    def fitting_iterations(self,x):
        if x>0 and float(x).is_integer():
            self.__FittingIterations=x
        else:
            raise ValueError("Fitting iterations must be positive integer")

    @property
    def step_size(self):
        '''
        # Parameter for ceres. Not entirely sure how this is used,
            #	beyond that it's used for computing derivatives.
        '''
        return self.__StepSize

    @step_size.setter
    def step_size(self, x):
        self.__StepSize=x

    @property
    def der_eps(self):
        '''
        # Parameter for ceres. Not entirely sure how this is used,
            #	beyond that it's used for computing derivatives.
        '''
        return self.__DerEps

    @der_eps.setter
    def der_eps(self, x):
        self.__DerEps=x

    @property
    def minimizer_type(self):
        '''
        Required.
        Valid values: ["Line Search","Trust Region"]
            #	If "Trust Region", TrustRegionStrategyType must be valid.
            #	If "Line Search", lineSearchType must be valid.
        '''
        return self.__MinimizerType

    @minimizer_type.setter
    def minimizer_type(self, min):
        if min not in ["Line Search","Trust Region"]:
            raise ValueError("minimizer type must be Line Search or Trust Region")
        self.__MinimizerType=min

    @property
    def trust_region_strategy_type(self):
        '''
            # ["Levenberg-Marquardt","Dogleg"]
            #	If "Dogleg", then DoglegType must be valid.
        '''
        return self.__TrustRegionStrategyType

    @trust_region_strategy_type.setter
    def trust_region_strategy_type(self, strat):
        if strat!="":
            if strat not in ["Levenberg-Marquardt","Dogleg"]:
                raise ValueError("Trust region strategy must be either Levenberg-Marquadt or Dogleg")
        self.__TrustRegionStrategyType=strat

    @property
    def dogleg_type(self):
        '''
        valid values: # ["Traditional Dogleg","Subspace Dogleg"]
        '''
        return self.__DoglegType

    @dogleg_type.setter
    def dogleg_type(self, dog):
        if dog!="":
            if dog not in ["Traditional Dogleg","Subspace Dogleg"]:
                raise ValueError("dogleg type must be Traditional or Subspace Dogleg")
        self.__DoglegType=dog

    @property
    def line_search_type(self):
        # ["Armijo","Wolfe"]
        #	If "Armijo", then LineSearchDirectionType cannot be ["BFGS","L-BFGS"].
        return self.__LineSearchType

    @line_search_type.setter
    def line_search_type(self, line):
        if line!="":
            if line not in ["Armijo","Wolfe"]:
                raise ValueError("line search type must be Armijo or Wolfe")
        self.__LineSearchType=line

    @property
    def line_search_direction_type(self):
        '''
        # ["Steepest Descent","Nonlinear Conjugate Gradient","L-BFGS","BFGS"]
        #	If "Nonlinear Conjugate Gradient", NonlinearConjugateGradientType
        #	must be valid.
        '''
        return self.__LineSearchDirectionType

    @line_search_direction_type.setter
    def line_search_direction_type(self, dir):
        if dir!="":
            if dir not in ["Steepest Descent","Nonlinear Conjugate Gradient","L-BFGS","BFGS"]:
                raise ValueError("line search direction type must be "
                                 "Steepest Descent, Nonlinear Conjugate Gradient,L-BFGS, or BFGS")
        self.__LineSearchDirectionType=dir

    @property
    def nonlinear_conjugate_gradient_type(self):
        '''
            # ["Fletcher Reeves","Polak Ribirere","Hestenes Stiefel"]
            #	See ceres documentation.
        '''
        return self.__NonlinearConjugateGradientType

    @nonlinear_conjugate_gradient_type.setter
    def  nonlinear_conjugate_gradient_type(self, grad):
        if grad!="":
           if grad not in ["Fletcher Reeves","Polak Ribirere","Hestenes Stiefel"]:
               raise ValueError("gradient type must be Fletcher Reeves, Polak Ribirere, or Hestenes Stiefel")
        self.__NonlinearConjugateGradientType=grad


    def serialize(self):
        self.validate()  # before returning dictionary to be used in further calculation,
        # check that values in dictionary are valid.
        return {

            "Convergence": self.convergence,
            "XRayResidualsType": self.x_ray_residuals_type,
            "FittingIterations": self.fitting_iterations,
            "StepSize": self.step_size,
            "DerEps": self.der_eps,
            
            "LossFunction": self.loss_function,
            "LossFuncPar1": self.loss_func_param_one,
            "LossFuncPar2": self.loss_func_param_two,
            
            "MinimizerType": self.minimizer_type,

            "TrustRegionStrategyType": self.trust_region_strategy_type,

            "DoglegType": self.dogleg_type,

            "LineSearchType": self.line_search_type,
            "LineSearchDirectionType": self.line_search_direction_type,
            "NonlinearConjugateGradientType": self.nonlinear_conjugate_gradient_type,




        }

    def validate(self):
        if self.minimizer_type == "Trust Region":
            if self.trust_region_strategy_type not in ["Levenberg-Marquardt", "Dogleg"]:
                raise ValueError("If minimizer type is trust region, must set trust_region_strategy_type")
            if self.trust_region_strategy_type == "Dogleg":
                if self.dogleg_type not in ["Traditional Dogleg", "Subspace Dogleg"]:
                    raise ValueError("If trust region strategy type is dogleg, must set dogleg_type")

        if self.minimizer_type == "Line Search":
            if self.line_search_type not in ["Armijo", "Wolfe"]:
                raise ValueError("If trust region type is line search, must set line_search_type")
            if self.line_search_type == "Armijo":
                if self.line_search_direction_type in ["BFGS", "L-BFGS"]:
                    raise ValueError("If line search type is Armijo, line search direction type cannot be BFGS, L-BFGS")
            if self.line_search_direction_type == "Nonlinear Conjugate Gradient":
                if self.nonlinear_conjugate_gradient_type not in ["Fletcher Reeves", "Polak Ribirere",
                                                                  "Hestenes Stiefel"]:
                    raise ValueError(
                        "if line search direction type is nonlinear conjugate gradient, must set nonlinear_conjugate_gradient_type")

    def load_from_dictionary(self, json):
        self.convergence=json["Convergence"] 
        self.x_ray_residuals_type=json["XRayResidualsType"]
        self.fitting_iterations=json["FittingIterations"]
        self.step_size=json["StepSize"]
        self.der_eps= json["DerEps"] 

        self.loss_function=json["LossFunction"] 
        self.loss_func_param_one=json["LossFuncPar1"]
        self.loss_func_param_two=json["LossFuncPar2"]

        self.minimizer_type=json["MinimizerType"]

        self.trust_region_strategy_type=json["TrustRegionStrategyType"]
        self.dogleg_type=json["DoglegType"]

        self.line_search_type=json["LineSearchType"]
        self.line_search_direction_type=json["LineSearchDirectionType"]
        self.nonlinear_conjugate_gradient_type=json["NonlinearConjugateGradientType"]
        self.validate()

    def __str__(self):
        return (str(self.serialize()))

class State:
    def __init__(self):
        self.DomainPreferences = DomainPreferences()
        self.FittingPreferences = FittingPreferences()
        self.__Viewport = { #This is totally irrelevant and is here for legacy purposes only
                              "Axes_at_origin": True,
                              "Axes_in_corner": True,
                              "Pitch": 35.264389038086,
                              "Roll": 0,
                              "Yaw": 225.00001525879,
                              "Zoom": 8.6602535247803,
                              "cPitch": 35.264389038086,
                              "cRoll": 0,
                              "cpx": -4.9999990463257,
                              "cpy": -5.0000004768372,
                              "cpz": 4.9999995231628,
                              "ctx": 0,
                              "cty": 0,
                              "ctz": 0
                          }
        self.Domain = Domain()
        self._filenames = []

    def load_from_dictionary(self, json):
        self.DomainPreferences.load_from_dictionary(json["DomainPreferences"])
        self.FittingPreferences.load_from_dictionary(json["FittingPreferences"])
        try:
            self.__Viewport = json["Viewport"]
        except:
            pass  # no one cares about viewport
        self.Domain = Domain()
        self.Domain.load_from_dictionary(json["Domain"])

    def serialize(self):
        self._validate_model_tree()
        return {
            "DomainPreferences": self.DomainPreferences.serialize(),
            "FittingPreferences": self.FittingPreferences.serialize(),
            "Viewport": self.__Viewport,
            "Domain": self.Domain.serialize()
        }

    def export_all_parameters(self, filename):
        with open(filename, 'w') as file:
            file.write(json.dumps(self.serialize()))

    def __str__(self):
        return (
            "Domain Preferences: " + str(self.DomainPreferences)
            + "\n"
            + "Fitting Preferences: " + str(self.FittingPreferences)
            + "\n"
            + "Domain: " + str(self.Domain)
        )

    def get_model(self, name_or_ptr):
        if not isinstance(name_or_ptr, int) and not isinstance(name_or_ptr, str):
            raise ValueError("Either provide an integer model pointer or a string model name")

        num_found = 0
        if self.Domain.model_ptr == name_or_ptr:
            result = self.Domain
            num_found += 1
        for population in self.Domain.populations:
            if population.model_ptr == name_or_ptr:
                result = population
                num_found += 1
            for model in population.models:
                if model.name == name_or_ptr or model.model_ptr == name_or_ptr:
                    result = model
                    num_found += 1
        if num_found == 0:
            raise (Exception("Model with that identifier not found"))
        if num_found > 1:
            raise (Exception("Model identifier not unique. More than one model found"))
        return result

    def get_models_by_type(self, type):
        models = []
        for population in self.Domain.Children:
            for model in population.Children:
                if model.type_name == type:
                    models.append(model)
        return models

    def get_mutable_parameter_values(self):
        params = self.get_mutable_params()
        param_array = []
        sigma_array = []
        constr_min = []
        constr_max = []
        for model_params in params:
            for param in model_params:
                param_array.append(param.value)
                sigma_array.append(param.sigma)
                constr_min.append(param.constraints.MinValue)
                constr_max.append(param.constraints.MaxValue)
        return param_array

    def set_mutable_parameter_values(self, param_vals_array):
        param_index = 0
        params = self.get_mutable_params()

        for model_params in params:
            for param in model_params:
                param.value = param_vals_array[param_index]
                param_index += 1

    def get_mutable_params(self):
        '''
        return array of arrays of all mutable parameters in tree
        '''

        def _recursive(param_array, model):
            mut=model.get_mutable_params()
            if mut:
                param_array.append(mut)
            try:
                for child in model.Children:
                    models_set = _recursive(param_array, child)
            except AttributeError:
                pass
            return param_array

        res = _recursive([], self.Domain)
        return [par for par in res if par is not None]

    def _all_models_indices(self):
        def _recursive(models_set, model):
            if model.model_ptr in models_set:
                raise ValueError("There are non-unique model pointers")
            models_set.add(model.model_ptr)
            try:
                for child in model.Children:
                    models_set = _recursive(models_set, child)
            except AttributeError:
                pass
            return models_set

        return _recursive(set(), self.Domain)

    def _get_all_filenames(self):
        #TODO: This is veyr not up to date with new file name passing
        def _recursive(model):
            try:
                self._filenames += model.filenames
            except AttributeError:
                pass
            try:
                for child in model.Children:
                    _recursive(child)
            except AttributeError:
                pass

        _recursive(self.Domain)
        return self._filenames

    def _validate_model_tree(self):
        # TODO: add other validations beyond model ptr unqiueness
        '''
        validations that need to be added:
        layers between min and max allowed amount
        children only on models with children, parameters only on models with parameters
        only parameters that exist in the model allowed
        !!model_ptr must be unique!!

        '''
        self._all_models_indices()

    def add_model(self, model, population_index=0):
        self.Domain.populations[population_index].Children.append(model)

    def add_amplitude(self, amplitude, population_index=0):
        from dplus.DataModels.models import AMP
        if not isinstance(amplitude, Amplitude):
            raise ValueError("add_amplitude can only be called on Amplitudes created from the dplus.Amplitudes.Amplitude class")
        if not amplitude.filename:
            raise ValueError("you must save the Amplitude to a file before adding it to the parameter tree")

        A = AMP(amplitude.filename)

        if not self.DomainPreferences.use_grid:
            self.DomainPreferences.use_grid=True
            print("Set Domain Preferences use_grid to True")

        if self.DomainPreferences.grid_size!=amplitude.grid_size:
            self.DomainPreferences.grid_size=amplitude.grid_size
            print("Set DomainPerefences grid_size to "+str(amplitude.grid_size))

        if self.DomainPreferences.q_max!=amplitude.q_max:
            self.DomainPreferences.q_max=amplitude.q_max
            print("Set DomainPreferences q_max to "+str(amplitude.q_max))

        self.add_model(A, population_index)
        return A
