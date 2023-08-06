from power_models_wrapper.data_transformation.abstract_filter import AbstractFilter

class AllPassFilter(AbstractFilter):

    def filter(self, data_dictionary):
        return data_dictionary;
