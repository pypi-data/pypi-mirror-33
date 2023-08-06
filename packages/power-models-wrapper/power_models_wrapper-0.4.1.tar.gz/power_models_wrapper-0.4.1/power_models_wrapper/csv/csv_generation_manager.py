from power_models_wrapper.csv.csv_generator import CsvGenerator
from power_models_wrapper.csv.aggregate_csv_generator import AggregateCsvGenerator

class CsvGenerationManager:

    def generate(self, data_dictionary):

        csv_generator_for_aggregate = AggregateCsvGenerator()
        result_for_aggregate = csv_generator_for_aggregate.generate(data_dictionary)

        csv_generator_for_nodes = CsvGenerator()
        result_for_nodes = csv_generator_for_nodes.generate(data_dictionary)

        result = {"result_aggregate": result_for_aggregate,
                  "result_nodes": result_for_nodes}

        return result
