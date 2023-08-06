# encoding: utf-8

import logging_helper
import unittest
import json
import os
from conversionutil import workbook_to_json

logging = logging_helper.setup_logging()



class TestWorkBookToJson(unittest.TestCase):

    def normalise_path(self,
                       path):
        return os.path.join(self.test_base_dir, os.sep.join(path.split(u'/')))

    def setUp(self):
        self.test_base_dir = os.path.dirname(os.path.realpath(__file__))

    # Test failure scenarios
    def test_single_sheet(self):
        filename = self.normalise_path(u'single_sheet.xlsx')
        result = workbook_to_json(filename=filename)
        result = json.loads(result)
        assert result[0].get("1") == "A"
        assert result[0].get("2") == "B"
        assert result[0].get("3") == "C"

    # Test failure scenarios
    def test_strip_false(self):
        filename = self.normalise_path(u'single_sheet.xlsx')
        result = workbook_to_json(filename=filename,
                                  strip=False)
        result = json.loads(result)
        assert result[0].get("1") == " A"
        assert result[0].get("2") == "B "
        assert result[0].get("3") == " C "

    # Test failure scenarios
    def test_multiple_sheets(self):
        filename = self.normalise_path(u'multiple_sheets.xlsx')
        result = workbook_to_json(filename=filename)
        result = json.loads(result)
        assert result.get(u'Sheet1')[0].get("A") == 1
        assert result.get(u'Sheet1')[0].get("B") == 2
        assert result.get(u'Sheet1')[0].get("C") == 3
        assert result.get(u'Sheet1')[1].get("A") == 4
        assert result.get(u'Sheet1')[1].get("B") == 5
        assert result.get(u'Sheet1')[1].get("C") == 6
        assert result.get(u'Sheet2')[0].get("D") == 7
        assert result.get(u'Sheet2')[0].get("E") == 8
        assert result.get(u'Sheet2')[0].get("F") == 9


if __name__ == u'__main__':
    unittest.main()
