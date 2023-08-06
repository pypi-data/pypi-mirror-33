from power_models_wrapper.data_transformation.abstract_filter import AbstractFilter
import numpy as np

class UsageFilter(AbstractFilter):

    def __init__(self, filter_dictionary):
        self.filter_dictionary = filter_dictionary

    def filter(self, data_dictionary):

        #print("data_dictionary: %s" % (data_dictionary))

        result_data_dictionary = {}

        for variable_name, variable_data in data_dictionary.items():
            filter_data = self.filter_dictionary[variable_name]

            result_variable_data_list = []

            for variable_element, filter_value in zip(variable_data, filter_data):
                if filter_value == 1.0:
                   result_variable_data_list.append(variable_element.tolist())

            result_data_dictionary[variable_name] = np.array(result_variable_data_list)

        return result_data_dictionary
