import unittest
from core.utils.testrail import TestRail
from os import environ


class TestTestRailCheckGetTypeStatus(unittest.TestCase):
    def setUp(self):
        self.tr = TestRail()

    def test_check_status_api(self):
        environ['TESTRAIL_AUTOMATED_TYPE_API'] = '5'
        self.assertEqual(self.tr._get_test_type('api'), 5)

    def test_check_status_api_not_equal(self):
        environ['TESTRAIL_AUTOMATED_TYPE_API'] = '5'
        self.assertNotEqual(self.tr._get_test_type('api'), '5')

    def test_check_status_gui(self):
        environ['TESTRAIL_AUTOMATED_TYPE_GUI'] = '6'
        self.assertEqual(self.tr._get_test_type('ui'), 6)

    def test_check_status_gui_not_equal(self):
        environ['TESTRAIL_AUTOMATED_TYPE_GUI'] = '6'
        self.assertNotEqual(self.tr._get_test_type('ui'), '6')

    def test_check_status_none(self):
        environ['TESTRAIL_AUTOMATED_TYPE_NONE'] = '0'
        self.assertEqual(self.tr._get_test_type('test'), 0)


if __name__ == '__main__':
    unittest.main()
