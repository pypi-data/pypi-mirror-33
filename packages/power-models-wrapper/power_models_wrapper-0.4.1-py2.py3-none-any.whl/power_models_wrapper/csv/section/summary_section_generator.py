import numpy as np
import pandas as pd

class SummarySectionGenerator:

    SECTION_TITLE = '+++ Summary +++'
    SUBSECTION_INDICES = {"dg_investment_table_dercam_ui": ['Continuous Duty Technology', 'Node'],
                          "pv_investment_table_dercam_ui": ['Technology', 'Node']}
    SORTING_ORDER = {"dg_investment_table_dercam_ui": ['Node', 'Continuous Duty Technology'],
                     "pv_investment_table_dercam_ui": ['Node', 'Technology']}
    CSV_COLUMNS = {"dg_investment_table_dercam_ui": ['Capacity (kW)', 'Existing Units', 'Age', 'New Units', 'Lifetime', 'Total Capacity'],
                   "pv_investment_table_dercam_ui": ['Existing Capacity (kW)', 'Age', 'New Capacity', 'Lifetime', 'Size (m^2)', 'Total Capacity']}
    PREFIX_VALUES = {"Node": "node"}

    def get_summary_section_csv(self, data_dictionary, variable_titles):

        section_title = f"{self.SECTION_TITLE}\n"

        main_data_dictionary = dict(filter(lambda items: items[0] not in self.SUBSECTION_INDICES.keys(), data_dictionary.items()))
        #main_data_dictionary = {key: value for key, value in data_dictionary.items() if key not in self.SUBSECTION_INDICES.keys()}

        main_csv_list = [variable_titles[key] + ',' + str(value) for key, value in main_data_dictionary.items()]
        main_csv_content = "\n".join(main_csv_list) + '\n'

        subsection_data_dictionary = dict(filter(lambda items: items[0] in self.SUBSECTION_INDICES.keys(), data_dictionary.items()))
        #subsection_data_dictionary = {key: value for key, value in data_dictionary.items() if key in self.SUBSECTION_INDICES.keys()}

        subsection_csv_content = ""
        for subsection_key, subsection_data in subsection_data_dictionary.items():
            subsection_title = variable_titles[subsection_key]
            subsection_csv_content += f"++++++ {subsection_title} ++++++\n"
            subsection_csv_content += self.get_summary_subsection_csv(subsection_data, subsection_key)

        return section_title + main_csv_content + subsection_csv_content

    def get_summary_subsection_csv(self, input_data, subsection_type):
        data = self.convert_input_data(input_data, subsection_type)
        return data.to_csv(index = self.does_csv_include_index(), columns = self.CSV_COLUMNS[subsection_type])

    def convert_input_data(self, input_data, subsection_type):

        data_frame = pd.DataFrame(input_data)
        converted_data = data_frame.transpose()
        #converted_data = converted_data.sort_index()
        converted_data.sort_values(self.SORTING_ORDER[subsection_type], inplace = True)
        #converted_data['Node'] = "node" + converted_data['Node'].astype(str)
        self.__prefix_value(converted_data)
        converted_data.set_index(self.SUBSECTION_INDICES[subsection_type], inplace = True)

        return converted_data

    def does_csv_include_index(self):
        return True

    def __prefix_value(self, data_frame):
        for column_name, prefix_value in self.PREFIX_VALUES.items():
            data_frame[column_name] = prefix_value + data_frame[column_name].astype(str)
