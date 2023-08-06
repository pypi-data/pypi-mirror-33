from power_models_wrapper.csv.section.summary_section_generator import SummarySectionGenerator

class AggregateSummarySectionGenerator(SummarySectionGenerator):

    CSV_COLUMNS = {"dg_investment_table_dercam_ui": ['Capacity (kW)', 'Existing Units', 'New Units', 'Total Capacity'],
                   "pv_investment_table_dercam_ui": ['Existing Capacity (kW)', 'New Capacity', 'Size (m^2)', 'Total Capacity']}

    def convert_input_data(self, input_data, subsection_type):
        converted_data = super().convert_input_data(input_data, subsection_type)
        aggregated_data = converted_data.loc[:, self.CSV_COLUMNS[subsection_type]].sum().to_frame().T
        return aggregated_data

    def does_csv_include_index(self):
        return False
