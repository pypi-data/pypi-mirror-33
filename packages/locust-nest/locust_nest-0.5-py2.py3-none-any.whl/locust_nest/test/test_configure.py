import unittest
from mock import patch
from locust_nest.test import DATA_PATH
from locust_nest.configure import make_config
import sys


class conditional_decorator(object):
    def __init__(self, dec, condition):
        self.decorator = dec
        self.condition = condition

    def __call__(self, func):
        if not self.condition:
            # Return the function unchanged, not decorated.
            return func
        return self.decorator(func)


class TestConfigure(unittest.TestCase):
    @conditional_decorator(patch('__builtin__.raw_input', return_value=1), sys.version_info[0] < 3)
    @conditional_decorator(patch('builtins.input', return_value=1), sys.version_info[0] >= 3)
    def test_make_config(self, input):
        config_without_tasksets = make_config(DATA_PATH)
        no_tasksets = {'locusts': {'ExampleModelLocust': 1}, 'total_locusts': 1, 'total_tasksets': 0, 'tasksets': {}}
        self.assertEqual(config_without_tasksets,no_tasksets)
        config_without_tasksets = make_config(DATA_PATH, False)
        self.assertEqual(config_without_tasksets, no_tasksets)
        config = make_config(DATA_PATH, True)
        with_tasksets = {'locusts': {'ExampleModelLocust': 1}, 'total_locusts': 1, 'total_tasksets': 1, 'tasksets': {'ExampleModel':1}}
        self.assertEqual(config, with_tasksets)

if __name__=="__main__":
    unittest.main()