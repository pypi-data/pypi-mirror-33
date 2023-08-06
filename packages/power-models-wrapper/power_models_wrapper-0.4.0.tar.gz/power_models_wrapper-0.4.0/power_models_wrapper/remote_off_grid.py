#from subprocess import run, PIPE
from power_models_wrapper.formulation_type import FormulationType
from power_models_wrapper.csv.csv_generation_manager import CsvGenerationManager
from power_models_wrapper.julia_preparation import JuliaPreparation

class RemoteOffGrid:

    def __init__(self):
        #pass
        #self.__julia_object = julia.Julia()
        #self.__julia_object.using("RemoteOffGridMicrogrids")
        julia_preparation = JuliaPreparation()
        self.__julia_object = julia_preparation.get_julia_object()

    def run(self, input_data_file_path):

        data_from_julia_code = self.run_julia_code(input_data_file_path)

        csv_generation_manager = CsvGenerationManager()
        result = csv_generation_manager.generate(data_from_julia_code)

        return result

    def run_julia_code(self, input_data_file_path):

        julia_code = "run_model(\"" + input_data_file_path + "\")"

        #print("julia_code: %s" % (julia_code))

        data_from_julia_code = self.__julia_object.eval(julia_code)

        return data_from_julia_code
