import unittest
from power_models_wrapper.optimal_power_flow import OptimalPowerFlow
import os
from power_models_wrapper.formulation_type import FormulationType

class TestOptimalPowerFlow(unittest.TestCase):

    def test_run_for_ac(self):

        input_matlab_data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tests/power_models_wrapper/fixtures/files/case3.m"))

        optimal_power_flow = OptimalPowerFlow()
        result = optimal_power_flow.run(input_matlab_data_file_path, formulation_type = FormulationType.ac)

        #print("result: %s)" % (result))

        self.assertEqual(result["solver"], "Ipopt.IpoptSolver")
        self.assertAlmostEqual(result["objective"], 5906, delta = 1)
