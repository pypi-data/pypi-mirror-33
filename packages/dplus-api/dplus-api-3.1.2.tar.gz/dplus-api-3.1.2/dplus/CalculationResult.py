from collections import OrderedDict
import pprint
import json

class CalculationResult(object):
    '''
    Stores the various aspects of the result for further manipulation
    '''
    def __init__(self, calc_data, result, job):
        self._raw_result = result #a json
        self._job=job #used for getting amps and pdbs
        self._calc_data = calc_data #gets x for getting graph. possibly also used for fitting.
        self._parse_headers() #sets self._headers to a list of headers
        self._get_graph() #creates an ordered dict, key x val y.
        self._get_parameter_tree() #right now just returns value from result. #TODO: should return python-useful fitting result

    def __str__(self):
        return pprint.pformat(self._raw_result)

    @property
    def y(self):
        #TODO: replace with something better
        return self._raw_result['Graph']

    def _get_parameter_tree(self):
        #TODO: replace with something better
        try:
            self._parameter_tree=self._raw_result['ParameterTree']
        except KeyError: #paramtertree does not exist in generate results
            pass

    def _parse_headers(self):
        header_dict = OrderedDict()
        try:
            headers=self._raw_result['Headers']
            for header in headers:
                header_dict[header['ModelPtr']] = header['Header']
        except: #TODO: headers don't appear in fit results?
            pass #regardless, I'm pretty sure no one cares about headers anyway
        self._headers=header_dict

    def _get_graph(self):
        graph = OrderedDict()
        x=self._calc_data.x
        try:
            if len(x)!=len(self._raw_result['Graph']):
                raise ValueError("Result graph size mismatch")
            for i in range(len(x)):
                graph[x[i]] = self._raw_result['Graph'][i]
        except KeyError: #sometimes Fit doesn't return a graph. Also every time Generate crashes.
            print("No graph returned")
        self._graph=graph

    @property
    def headers(self):
        return self._headers

    @property
    def graph(self):
        return self._graph

    @property
    def parameter_tree(self):
        return self._parameter_tree

    def get_pdb(self, model_ptr, destination_folder=None):
        return self._job._get_pdb(model_ptr, destination_folder)

    def get_amp(self, model_ptr, destination_folder=None):
        return self._job._get_amp(model_ptr, destination_folder)

    @property
    def error(self):
        if "error" in self._raw_result:
            return self._raw_result["error"]
        return {"code":0, "message":"no error"}

    def save_to_out_file(self, filename):
        with open(filename, 'w') as out_file:
            domain_preferences = self._calc_data.state.DomainPreferences
            out_file.write("# Integration parameters:\n")
            out_file.write("#\tqmax\t{}\n".format(domain_preferences.q_max))
            out_file.write("#\tOrientation Method\t{}\n".format(domain_preferences.orientation_method))
            out_file.write("#\tOrientation Iterations\t{}\n".format(domain_preferences.orientation_iterations))
            out_file.write("#\tConvergence\t{}\n\n".format(domain_preferences.convergence))
            for value in self.headers.values():
                out_file.write(value)
            for key, value in self.graph.items():
                out_file.write('{:.5f}\t{:.20f}\n'.format(key,value))
            out_file.close()


#TODO: add to fit results
'''
    def get_simple_json(self):
        
        #the simple json is so titled simply because that's what it's called in the dplus paramter tree converter
        #it is used to populate the parametertree returned by fit
        
        orientation_dict = {
            "Monte Carlo (Mersenne Twister)": 0,
            "Adaptive (VEGAS) Monte Carlo": 1,
            "Adaptive Gauss Kronrod": 2,
            "Direct Computation - MC": 3,
            "Monte Carlo (Sobol) - unimplemented": 4
        }

        basic_dict = self.Domain.basic_json_params(self.DomainPreferences.use_grid)

        # the populations have domain preferences added as parameters (i have no idea why),
        # and hence their dictionary needs to be modified here in the state
        # this is not necessarily correct for singleGeometry, I'm not sure how to handle that
        for population_dict in basic_dict["Submodels"]:
            population_dict["Parameters"].append(Parameter(self.DomainPreferences.orientation_iterations).serialize())
            population_dict["Parameters"].append(Parameter(self.DomainPreferences.grid_size).serialize())
            population_dict["Parameters"].append(Parameter(1).serialize()) if self.DomainPreferences.use_grid else \
                population_dict["Parameters"].append(Parameter(0).serialize())  ##needs modification to integer
            population_dict["Parameters"].append(Parameter(self.DomainPreferences.convergence).serialize())
            population_dict["Parameters"].append(Parameter(self.DomainPreferences.q_max).serialize())
            population_dict["Parameters"].append(Parameter(orientation_dict[self.DomainPreferences.orientation_method]).serialize())  ##expects to receive an ENUM translation

        return basic_dict

'''