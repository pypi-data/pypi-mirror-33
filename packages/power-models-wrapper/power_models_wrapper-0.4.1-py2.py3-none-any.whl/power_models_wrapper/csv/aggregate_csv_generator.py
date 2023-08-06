from power_models_wrapper.csv.csv_generator import CsvGenerator
from power_models_wrapper.csv.section.aggregate_summary_section_generator import AggregateSummarySectionGenerator

class AggregateCsvGenerator(CsvGenerator):

    # TODO: Move these to configuration file. (This TODO is written despite the fact that it is obvious that it has been the intention from the beginning.)
    VARIABLE_TYPES = {"total_cost_dercam_ui": "summary",
                      "dg_investment_table_dercam_ui": "summary",
                      "pv_investment_table_dercam_ui": "summary",
                      "dg_output_agg_dercam_ui": "timeseries",
                      "pv_output_agg_dercam_ui": "timeseries",
                      "bat_output_agg_dercam_ui": "timeseries",
                      "bat_input_agg_dercam_ui": "timeseries",
                      "new_lines_dercam_ui": "new_lines"}
    VARIABLE_TITLES = {"total_cost_dercam_ui": "Total Cost",
                       "dg_investment_table_dercam_ui": "Generator Investment",
                       "pv_investment_table_dercam_ui": "PV Investment",
                       "dg_output_agg_dercam_ui": "Aggregated Generator Active Power Output",
                       "pv_output_agg_dercam_ui": "Aggregated PV Active Power Output",
                       "bat_output_agg_dercam_ui": "Aggregated Battery Active Power Output (Discharge)",
                       "bat_input_agg_dercam_ui": "Aggregated Battery Active Power Input (Charge)",
                       "new_lines_dercam_ui": "New Lines"}

    def generate_for_given_variable(self, writer, data_dictionary, key, value, number_of_months_in_data = 12):
        if value == "timeseries":
            self.get_timeseries_section_generator().write_rows_for_timeseries(writer, data_dictionary[key], number_of_months_in_data)
        elif value == "new_lines":
            self.get_new_lines_section_genertor().write_rows_for_new_lines(writer, data_dictionary[key])

    def day_type_title_row(self, index, number_of_months_in_data, node_number = 0):
        return [self.DAY_TYPE[self.get_index_for_day_type(index, number_of_months_in_data)]]

    def get_summary_section_generator(self):
        if self.summary_section_generator == None:
            self.summary_section_generator = AggregateSummarySectionGenerator()
        return self.summary_section_generator
