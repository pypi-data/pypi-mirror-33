import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops.read_config import read_config, validate_config
from nikippe.displayserver import DisplayServer
import nikippe.schema.sequentialchart
import nikippe.schema.bar
import nikippe.schema.digitalclock
import nikippe.schema.mqtttext
import nikippe.schema.statictext
import nikippe.schema.staticimage
import nikippe.schema.imagelist
import jsonschema


class TestValidateConfig(unittest.TestCase):
    def setUp(self):
        self.config = read_config(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) +
                                  "/tests_unit/config.yaml")

    def test_element_sequentialchart(self):
        validation_result = jsonschema.validate(
            self.config["display-server"]["renderer"]["elements"][0],
            nikippe.schema.sequentialchart.get_schema())
        self.assertIsNone(validation_result)

    def test_element_bar(self):
        validation_result = jsonschema.validate(
            self.config["display-server"]["renderer"]["elements"][1],
            nikippe.schema.bar.get_schema())
        self.assertIsNone(validation_result)

    def test_element_digitalclock(self):
        validation_result = jsonschema.validate(
            self.config["display-server"]["renderer"]["elements"][2],
            nikippe.schema.digitalclock.get_schema())
        self.assertIsNone(validation_result)

    def test_element_mqtttext(self):
        validation_result = jsonschema.validate(
            self.config["display-server"]["renderer"]["elements"][3],
            nikippe.schema.mqtttext.get_schema())
        self.assertIsNone(validation_result)

    def test_element_statictext(self):
        validation_result = jsonschema.validate(
            self.config["display-server"]["renderer"]["elements"][4],
            nikippe.schema.statictext.get_schema())
        self.assertIsNone(validation_result)

    def test_element_staticimage(self):
        validation_result = jsonschema.validate(
            self.config["display-server"]["renderer"]["elements"][5],
            nikippe.schema.staticimage.get_schema())
        self.assertIsNone(validation_result)

    def test_element_imagelist(self):
        validation_result = jsonschema.validate(
            self.config["display-server"]["renderer"]["elements"][6],
            nikippe.schema.imagelist.get_schema())
        self.assertIsNone(validation_result)

    def test_validate_config(self):
        validation_result = validate_config(self.config, DisplayServer._get_schema())
        self.assertIsNone(validation_result)


if __name__ == '__main__':
    unittest.main()
