import unittest
from power_models_wrapper.remote_off_grid import RemoteOffGrid
import os

class TestRemoteOffGrid(unittest.TestCase):

    #@unittest.skip
    def test_run_model(self):

        #input_data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures/files/LANL_INPUT_CORDOVA_LATEST.xlsx"))
        input_data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures/files/LANL_INPUT_REAL.xlsx"))

        #print("input_data_file_path: %s" % (input_data_file_path))

        remote_off_grid = RemoteOffGrid()
        result = remote_off_grid.run(input_data_file_path)

        print("result['result_aggregate']: %s)" % (result['result_aggregate']))
        print("result['result_nodes']: %s)" % (result['result_nodes']))

        # TODO: Add better assertions:
        self.assertIn("Summary", result["result_aggregate"])
        self.assertIn("Total Cost", result["result_aggregate"])
        self.assertIn("Generator Investment", result["result_aggregate"])
        self.assertIn("PV Investment", result["result_aggregate"])
        self.assertIn("Aggregated Generator Active Power Output", result["result_aggregate"])
        self.assertIn("Aggregated PV Active Power Output", result["result_aggregate"])
        self.assertIn("Aggregated Battery Active Power Output (Discharge)", result["result_aggregate"])
        self.assertIn("Aggregated Battery Active Power Input (Charge)", result["result_aggregate"])
        self.assertNotIn("node6", result["result_aggregate"])
        self.assertIn("Summary", result["result_nodes"])
        self.assertIn("Total Cost", result["result_nodes"])
        self.assertIn("Generator Investment", result["result_nodes"])
        self.assertIn("PV Investment", result["result_nodes"])
        self.assertIn("Generator Active Power Output", result["result_nodes"])
        self.assertIn("PV Active Power Output", result["result_nodes"])
        self.assertIn("Battery Active Power Output (Discharge)", result["result_nodes"])
        self.assertIn("Battery Active Power Input (Charge)", result["result_nodes"])
        self.assertIn("Voltage", result["result_nodes"])
        self.assertIn("node5", result["result_nodes"])
        self.assertNotIn("node6", result["result_nodes"])

    @unittest.skip
    def test_run_julia_code(self):

        #input_data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures/files/LANL_INPUT_CORDOVA_LATEST.xlsx"))
        input_data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures/files/LANL_INPUT_REAL.xlsx"))

        #print("input_data_file_path: %s" % (input_data_file_path))

        remote_off_grid = RemoteOffGrid()
        data_from_julia_code = remote_off_grid.run_julia_code(input_data_file_path)

        print("data_from_julia_code: %s" % (data_from_julia_code))
        #print("type(data_from_julia_code): %s" % (type(data_from_julia_code)))
        #print("len(data_from_julia_code): %s" % (len(data_from_julia_code)))
        data_portion = data_from_julia_code["dg_investment_table_dercam_ui"]
        print("data_portion: %s" % (data_portion))
        print("type(data_portion): %s" % (type(data_portion)))
        print("len(data_portion): %s" % (len(data_portion)))
        #print("data_portion[0]: %s" % (data_portion[0]))
