import io
import csv
import numpy as np
from power_models_wrapper.data_transformation.all_pass_filter import AllPassFilter
from power_models_wrapper.csv.section.summary_section_generator import SummarySectionGenerator
from power_models_wrapper.csv.section.timeseries_section_generator import TimeseriesSectionGenerator
from power_models_wrapper.csv.section.new_lines_section_generator import NewLinesSectionGenerator

class CsvGenerator:

    # TODO: Move these to configuration file. (This TODO is written despite the fact that it is obvious that it has been the intention from the beginning.)
    DAY_TYPE = ["week", "peak", "weekend"]
    # Note: Since Python 3.6 dict type maintains the insertion order, put "summary" type first.
    #       If OrderedDict is needed for the future, supporting older version of Python, use OrderdDict at that time.
    VARIABLE_TYPES = {"total_cost_dercam_ui": "summary",
                      "dg_investment_table_dercam_ui": "summary",
                      "pv_investment_table_dercam_ui": "summary",
                      "dg_output_dercam_ui": "timeseries",
                      "pv_output_dercam_ui": "timeseries",
                      "bat_output_dercam_ui": "timeseries",
                      "bat_input_dercam_ui": "timeseries",
                      "voltage_dercam_ui": "timeseries",
                      "new_lines_dercam_ui": "new_lines"}
    VARIABLE_TITLES = {"total_cost_dercam_ui": "Total Cost",
                       "dg_investment_table_dercam_ui": "Generator Investment",
                       "pv_investment_table_dercam_ui": "PV Investment",
                       "dg_output_dercam_ui": "Generator Active Power Output",
                       "pv_output_dercam_ui": "PV Active Power Output",
                       "bat_output_dercam_ui": "Battery Active Power Output (Discharge)",
                       "bat_input_dercam_ui": "Battery Active Power Input (Charge)",
                       "voltage_dercam_ui": "Voltage",
                       "new_lines_dercam_ui": "New Lines",
                       "p_g": "Generator Active Power Output",
                       "p_pv": "PV Active Power Output",
                       "p_w": "Wind Active Power Output",
                       "p_b": "Battery Active Power Output",
                       "sc_b": "Battery State of Charge"}

    summary_section_generator = None
    __timeseries_section_generator = None
    __new_lines_section_genertor = None

    def __init__(self, filter = None):
        if filter == None:
            self.filter = AllPassFilter()
        else:
            self.filter = filter

    def generate(self, data_dictionary, variable_types = None, number_of_months_in_data = 12, number_of_day_type_in_data = 3):

        if variable_types == None:
            variable_types = self.VARIABLE_TYPES

        data_dictionary = self.__apply_filter(data_dictionary)

        summary_section_csv = self.generate_summary_section(data_dictionary, variable_types)

        output = io.StringIO()
        writer = csv.writer(output, quoting = csv.QUOTE_NONNUMERIC)

        for key, value in variable_types.items():
            if value != "summary":
                writer.writerow(["*** " + self.VARIABLE_TITLES[key]])
            self.generate_for_given_variable(writer, data_dictionary, key, value, number_of_months_in_data)

        return summary_section_csv + output.getvalue()

    def generate_summary_section(self, data_dictionary, variable_types):
        summary_data_dictionary = { key: data_dictionary[key] for key, value in variable_types.items() if value == "summary" }

        if summary_data_dictionary:
            return self.get_summary_section_generator().get_summary_section_csv(summary_data_dictionary, self.VARIABLE_TITLES)
        else:
            return ""

    def generate_for_given_variable(self, writer, data_dictionary, key, value, number_of_months_in_data = 12):

        # Note: Simple code for putting summary data. For summary subsection, this will be modified.
        #if value == "summary":
        #    writer.writerow([self.VARIABLE_TITLES[key], data_dictionary[key]])
        #elif value == "timeseries":
        if value == "timeseries":
            for node_index, node_array in enumerate(data_dictionary[key]):
                node_number = node_index + 1
                self.get_timeseries_section_generator().write_rows_for_timeseries(writer, node_array, number_of_months_in_data, node_number)
        elif value == "new_lines":
            self.get_new_lines_section_genertor().write_rows_for_new_lines(writer, data_dictionary[key])

    # Note: Made it public in order to access from unit test.
    def get_index_for_day_type(self, index, number_of_months_in_data):
        return index // number_of_months_in_data

    def day_type_title_row(self, index, number_of_months_in_data, node_number = 0):
        return ["node" + str(node_number), self.DAY_TYPE[self.get_index_for_day_type(index, number_of_months_in_data)]]

    def __apply_filter(self, data_dictionary):
       return self.filter.filter(data_dictionary)

    def get_summary_section_generator(self):
        if self.summary_section_generator == None:
            self.summary_section_generator = SummarySectionGenerator()
        return self.summary_section_generator

    def get_timeseries_section_generator(self):
        if self.__timeseries_section_generator == None:
            self.__timeseries_section_generator = TimeseriesSectionGenerator(self)
        return self.__timeseries_section_generator

    def get_new_lines_section_genertor(self):
        if self.__new_lines_section_genertor == None:
            self.__new_lines_section_genertor = NewLinesSectionGenerator()
        return self.__new_lines_section_genertor
