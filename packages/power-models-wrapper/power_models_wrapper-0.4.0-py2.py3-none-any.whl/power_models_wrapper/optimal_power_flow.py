#from subprocess import run, PIPE
from power_models_wrapper.formulation_type import FormulationType
from power_models_wrapper.julia_preparation import JuliaPreparation

class OptimalPowerFlow:

    def __init__(self):
        #pass
        #self.__julia_object = julia.Julia()
        #self.__julia_object.using('PowerModels')
        julia_preparation = JuliaPreparation()
        self.__julia_object = julia_preparation.get_julia_object()

    def run(self, input_matlab_data_file_path, formulation_type = FormulationType.ac):

        # TODO: Initial implementation of using PowerModels run method, using hardcoded solver:
        self.__julia_object.using('Ipopt')
        julia_code = self.__get_julia_run_method_name(formulation_type) + '("' + input_matlab_data_file_path + '", IpoptSolver())'
        result = self.__julia_object.eval(julia_code)

        #julia_method_call_code = 'result = ' + self.__get_julia_run_method_name(formulation_type) + '("' + input_matlab_data_file_path + '", IpoptSolver());'
        #julia_code = "using PowerModels; using Ipopt; " + julia_method_call_code + " println(result)"
        #result = run(["julia", "-e", julia_code], stdout = PIPE)

        return result

    def __get_julia_run_method_name(self, formulation_type):
        return "run_%(formulation_type)s_opf" % {'formulation_type':formulation_type.name}
