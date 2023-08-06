import numpy as np
from calendar import month_name
#from power_models_wrapper.csv.csv_generator import CsvGenerator

class TimeseriesSectionGenerator:

    # TODO: Move these to configuration file. (This TODO is written despite the fact that it is obvious that it has been the intention from the beginning.)
    TIME_STEPS = 24
    NUMBER_OF_MONTHS = 12

    def __init__(self, csv_generator):
        self.csv_generator = csv_generator

    def write_rows_for_timeseries(self, writer, data_array, number_of_months_in_data = 12, node_number = 0):
        divided_data = self.divide_for_timeseries(data_array)
        #print("divided_data: %s" % (divided_data))

        for index, data_row in enumerate(divided_data):
            if index % number_of_months_in_data == 0:
                writer.writerow(self.csv_generator.day_type_title_row(index, number_of_months_in_data, node_number))
            writer.writerow(data_row)

    def divide_for_timeseries(self, data):
        reshaped_data = np.reshape(data, (len(data) // self.TIME_STEPS, self.TIME_STEPS)).tolist()
        result_data_with_original_order = self.__add_month_name(reshaped_data)
        result_data = self.__rearrange_rows(result_data_with_original_order)

        return result_data

    def __add_month_name(self, reshaped_data):
        return [[month_name[index//len(self.csv_generator.DAY_TYPE) + 1]] + row_list for index, row_list in enumerate(reshaped_data)]

    def __rearrange_rows(self, data):
        result = []
        for index, day_type in enumerate(self.csv_generator.DAY_TYPE):
            result = result + data[index:len(data):len(self.csv_generator.DAY_TYPE)]
        return result;
