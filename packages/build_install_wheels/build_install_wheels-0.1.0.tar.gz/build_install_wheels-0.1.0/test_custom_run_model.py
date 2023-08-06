import sys
from unittest import TestCase

from custom_run_model import reload_run_save_result, resolve_params


class TestCustomRunModel(TestCase):
    def setUp(self):
        sys.argv[1:] = '--test_data_path=./../inputs/test.csv', \
                       '--model_config_file=./../inputs/model_config.json', \
                       '--output_scored_model=./../outputs/scored_model.csv', \
                       '--output_scored_model_config=./../outputs/scored_model_config.json'

    def test_reload_run_save_result(self):
        params = resolve_params()
        reload_run_save_result(*params)
