'''
A python implemention of the fitting algorithm, using scipy's optimization libraries
'''

from __future__ import print_function
from copy import deepcopy
from scipy import optimize
from dplus.CalculationInput import FitInput, GenerateInput
from dplus.CalculationResult import CalculationResult
from dplus.FileReaders import NumpyHandlingEncoder
import math
import json
import os
import numpy


#TODO: This needs to be synced with CalculationResult properly, instead of just being stuck here
class FitResult:
    def __init__(self, result, calc_data):
        '''
        :param result: the output json from a run of Generate
        :param calc_data: the CalculationInput we are getting a result from.
        required for the x's of the graph, and in the case of Fitting for the parameter tree as well
        '''
        self._raw_result = result
        self._calc_data = calc_data
        self._graph = self._get_graph()
        self._param_tree = self._calc_data._state.get_simple_json()

    #def to_dplus(self):
    #    return self._raw_result

    @property
    def graph(self):
        return self._graph

    def _get_graph(self):
        graph = OrderedDict()
        x = self._calc_data.x
        if len(x) != len(self._raw_result['Graph']):
            raise ValueError("Result graph size mismatch")
        for i in range(len(x)):
            graph[x[i]] = self._raw_result['Graph'][i]
        return graph

    @property
    def error(self):
        if "error" in self._raw_result:
            return self._raw_result["error"]
        return {"code":0, "message":"no error"}

    @property
    def parameter_tree(self):
        return self._param_tree


    def to_dplus(self):
        '''
        overwrites Result's to_dplus replacing it with the expected result from Fit
        :return: a dictionary with a Parameter Tree and a graph.
        '''
        dict = {
            "ParameterTree": self.parameter_tree,
            "Graph": self._raw_result['Graph']
        }
        return dict




class Fitter:
    def __init__(self, generate_runner):
        '''
        :param generate_runner: a LocalRunner or WebRunner used for running generation
        '''
        self._generate_runner=generate_runner

    def _input_to_array(self):
        '''
        from calculation input, build an array of mutable paramters
        :return:
        '''
        params= self._calc_input.get_mutable_params()
        param_array=[]
        sigma_array=[]
        constr_min=[]
        constr_max=[]
        for model_params in params:
            for param in model_params:
                param_array.append(param.value)
                sigma_array.append(param.sigma)
                # TODO: constraints
        return param_array, sigma_array

    def _array_to_input(self, param_array, calc_input):
        '''
        from optimized parameters, build a new calculation input
        :param param_array:
        :param calc_input:
        :return:
        '''
        param_index = 0
        params= calc_input.get_mutable_params()
        for model_params in params:
            for param in model_params:
                param.value= param_array[param_index]
                param_index+=1
        return calc_input


    def _run_generate(self, xdata, *params):
        '''
        send calculation input to generate, return scipyappropriate generate result
        :param xdata:
        :param params:
        :return:
        '''
        print("calling generate")
        input=self._array_to_input(params, self._generate_input)
        generate_results= self._generate_runner.generate(input)
        return self._evaluate_results(generate_results)

    def _evaluate_results(self, calc_result):
        #unsure if this function is necessary. was used when building fit algorithm stepbystep.
        # might be needed if this section becomes more complicated in the future
        self._y=calc_result.y
        return calc_result.y

    def _curve_fit(self):
        '''
        scipy.optimize.curve_fit(f, xdata, ydata, p0=None, sigma=None, absolute_sigma=False, check_finite=True, bounds=(inf, inf), method=None, jac=None, **kwargs)
        '''
        xdata=self._calc_input.x
        ydata=self._calc_input.y
        p0, sigma=self._input_to_array()

        #bounds = constraints, once added...
        method= 'lm'

        #sadly, no, this is for optimize, not for curve_fit:
        #options={"maxiter":self._calc_input.state.FittingPreferences["FittingIterations"], "disp":True}

        #kwargs to leastsquares...

        print("calling curve fit")
        popt, pcov= optimize.curve_fit(self._run_generate, xdata, ydata, p0=p0, method=method)

        print(p0)
        print(popt)
        return popt

    def run(self, calc_input):
        '''
        :param calc_input: a FitInput containing the input for the fit calculation
        :return: a FitResult containing the optimized parameters and the results of a generate on those parameters
        '''
        if not isinstance(calc_input, FitInput):
            raise ValueError("Fit expects to receive a FitInput")
        self._calc_input=calc_input
        self._generate_input= GenerateInput.load_from_FitInput(calc_input)
        # get best parameters
        best_opt= self._curve_fit()
        #convert parameters to an input
        best_input= self._array_to_input(best_opt, self._generate_input)
        # run generate one more time with best parameters, in order to have correct graph
        generate_results = self._generate_runner.generate(best_input)
        # create a FitResult from the best input (aka parameter results) and the graph results
        result = FitResult(best_input, generate_results._raw_result)
        return result



class FitRunner:
    '''
    a wrapper for the fitter that duplicates the filebased handling of all the other Runners
    '''
    def __init__(self, generate_runner,output_directory=None):
        self.fitter=Fitter(generate_runner)
        self._output_directory=output_directory

    def run(self,  calc_data):
        #initialize job as necessary:
        best_input=self._start()

        #get actual fitting results:
        result=self.fitter.run(calc_data)

        #finish job as necessary
        self._finish(result)
        return result


    def _start(self):
        if self._output_directory:
            filename = os.path.join(self._output_directory, "notrunning")
            with open(filename, 'w') as f:
                f.write("False")

            filename = os.path.join(self._output_directory, "job.json")
            jobstat = {"isRunning": True, "progress": 0.0, "code": 0, "addtnl_message":"frompython"}
            with open(filename, 'w') as outfile:
                json.dump(jobstat, outfile)

    def _finish(self, result):
        if self._output_directory:
            filename = os.path.join(self._output_directory, "data.json")
            with open(filename, 'w') as f:
                json.dump(result.to_dplus(), f, cls=NumpyHandlingEncoder)

            filename = os.path.join(self._output_directory, "job.json")
            jobstat = {"isRunning": False, "progress": 1.0, "code": 0, "addtnl_message":"frompython"}
            with open(filename, 'w') as outfile:
                json.dump(jobstat, outfile)

            filename = os.path.join(self._output_directory, "notrunning")
            with open(filename, 'w') as f:
                f.write("True")
