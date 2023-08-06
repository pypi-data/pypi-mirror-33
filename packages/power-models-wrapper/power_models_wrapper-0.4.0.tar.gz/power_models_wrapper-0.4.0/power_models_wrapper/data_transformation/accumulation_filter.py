from power_models_wrapper.data_transformation.abstract_filter import AbstractFilter

class AccumulationFilter(AbstractFilter):

    def __init__(self, filter_dictionary):
        self.filter_dictionary = filter_dictionary

    def filter(self, data_dictionary):
        pass
