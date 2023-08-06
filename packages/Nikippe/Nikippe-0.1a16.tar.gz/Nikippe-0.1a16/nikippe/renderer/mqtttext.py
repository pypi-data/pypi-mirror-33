from nikippe.renderer.aelementmqtt import AElementMQTT
from PIL import ImageFont
from PIL import ImageDraw
import os


class MQTTText(AElementMQTT):
    """
    Displays a dynamic text (single line). Every incoming mqtt message will be displayed

    additional yaml entries:
      font - path to font to be used
      size - font size
      string - text to be displayed
    """
    _font = None
    _size = None
    _string = None
    _current_value = None

    def __init__(self, config, update_available, mqtt_client, logger):
        AElementMQTT.__init__(self, config, update_available, mqtt_client, logger, __name__)

        self._font = os.path.expanduser(self._config["font"])
        if not os.path.isfile(self._font):
            self._logger.error("__init__ - font '{}' not found.".format(self._font))
            raise ValueError("__init__ - font '{}' not found.".format(self._font))
        self._size = self._config["size"]
        self._image_font = ImageFont.truetype(self._font, self._size)
        self._string = config["string"]

    def _topic_sub_handler(self, value):
        self._logger.info("MQTTText._topic_sub_handler - received value '{}'.".format(value))
        self._current_value = float(value)
        self._update_available.set()

    def _start(self):
        pass

    def _stop(self):
        pass

    def _update_image(self):
        self._logger.info("MQTTText.updateImage()")
        # clear image
        draw = ImageDraw.Draw(self.img)
        draw.rectangle((0, 0, self._width, self._height), fill=self._background_color)
        # write time
        text = ""
        if self._current_value is not None:
            text = self._string.format(self._current_value)
        self._logger.debug("MQTTText.updateImage() - string '{}', value '{}', text '{}'".
                          format(self._string, self._current_value, text))
        w, h = draw.textsize(text, self._image_font)
        x = int((self._width - w) / 2)
        y = int((self._height - h) / 2)
        draw.text((x, y), text, font=self._image_font, fill=self._foreground_color)

