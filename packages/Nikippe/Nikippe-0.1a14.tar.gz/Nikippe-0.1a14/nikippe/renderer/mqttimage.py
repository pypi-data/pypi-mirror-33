from io import BytesIO
from nikippe.renderer.aelementmqtt import AElementMQTT
from PIL import Image, ImageChops


class MQTTImage(AElementMQTT):
    """
    Displays images that are received via mqtt messages. Until first received image, background-color is used.

    additional yaml entries:
      offset_x - offset for image within element plane (optional, default=0)
      offset_y - offset for image within element plane (optional, default=0)
    """
    _mqtt_image = None
    _offset_x = None
    _offset_y = None

    def __init__(self, config, update_available, mqtt_client, logger):
        AElementMQTT.__init__(self, config, update_available, mqtt_client, logger, __name__)

        try:
            self._offset_x = self._config["offset_x"]
        except KeyError:
            self._offset_x = 0
        try:
            self._offset_y = self._config["offset_y"]
        except KeyError:
            self._offset_y = 0

    def _topic_sub_handler(self, value):
        self._logger.info("MQTTImage._topic_sub_handler - received value '{}'.".format(value))
        self._mqtt_image = Image.open(BytesIO(value))
        self._mqtt_image = self._mqtt_image.convert("L")
        self._update_available.set()

    def _start(self):
        pass

    def _stop(self):
        pass

    def _update_image(self):
        self._logger.info("MQTTImage.updateImage()")
        # clear result image
        self.img = ImageChops.constant(self.img, self._background_color)
        # place static image
        if self._mqtt_image is not None:
            self.img.paste(self._mqtt_image, box=(self._offset_x, self._offset_y))

