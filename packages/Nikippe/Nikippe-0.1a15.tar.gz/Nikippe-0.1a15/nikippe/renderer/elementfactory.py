from nikippe.renderer.sequentialchart import SequentialChart
from nikippe.renderer.digitalclock import DigitalClock
from nikippe.renderer.mqtttext import MQTTText
from nikippe.renderer.statictext import StaticText
from nikippe.renderer.bar import Bar
from nikippe.renderer.staticimage import StaticImage
from nikippe.renderer.imagelist import ImageList
import pelops.mylogger


class ElementFactory:
    """Factory class - creates silblings from AElement based on the provided config yaml structure."""

    @staticmethod
    def create_element(config_element, update_available, mqtt_client, logger):
        """
        Create the element that corresponds to the provided config yaml.

        :param config_element: config yaml structure for a single element
        :param update_available: Event instance. provided by renderer.
        :param mqtt_client: mqtt client instance
        :param logger: logger instance
        :return: instance of the created element
        """
        _logger = pelops.mylogger.get_child(logger, __name__)
        element = None
        if config_element["active"]:
            if config_element["type"].lower() == "sequentialchart":
                element = SequentialChart(config_element, update_available, mqtt_client, logger)
            elif config_element["type"].lower() == "statictext":
                element = StaticText(config_element, update_available, logger)
            elif config_element["type"].lower() == "staticimage":
                element = StaticImage(config_element, update_available, logger)
            elif config_element["type"].lower() == "digitalclock":
                element = DigitalClock(config_element, update_available, logger)
            elif config_element["type"].lower() == "mqtttext":
                element = MQTTText(config_element, update_available, mqtt_client, logger)
            elif config_element["type"].lower() == "imagelist":
                element = ImageList(config_element, update_available, mqtt_client, logger)
            elif config_element["type"].lower() == "bar":
                element = Bar(config_element, update_available, mqtt_client, logger)
            else:
                _logger.error("ElementFactory.create_element - unknown type '{}'".
                               format(config_element["type"].lower()))
                raise ValueError("ElementFactory.create_element - unknown type '{}'".
                                 format(config_element["type"].lower()))
        else:
            _logger.info("ElementFactory.create_element - skipping inactive element '{}.{}'.".
                      format(config_element["type"].lower(), config_element["name"]))

        return element

    @staticmethod
    def create_elements(config_elements, update_available, mqtt_client, logger):
        """
        Create all elements that are defined in the provided config.

        :param config_elements: config yaml for elements (array)
        :param update_available: Event instance provided by renderer
        :param mqtt_client: mqtt client instance
        :param logger: logger instance
        :return: list of all active elements
        """
        element_list = []
        _logger = pelops.mylogger.get_child(logger, __name__)

        _logger.info("ElementFactory.create_elements - start")

        for config_element in config_elements:
            element = ElementFactory.create_element(config_element, update_available, mqtt_client, logger)
            if element is not None:
                element_list.append(element)

        _logger.info("ElementFactory.create_elements - finished")

        return element_list


