from nikippe.renderer.aelement import AElement
from PIL import ImageFont
from PIL import ImageDraw
import os


class StaticText(AElement):
    """
    Displays a static text (single line).

    additional yaml entries:
      font - path to font to be used
      size - font size
      string - text to be displayed
    """
    _font = None
    _size = None
    _string = None

    def __init__(self, config, update_available, logger):
        AElement.__init__(self, config, update_available, logger, __name__)

        self._font = os.path.expanduser(self._config["font"])
        if not os.path.isfile(self._font):
            self._logger.error("__init__ - font '{}' not found.".format(self._font))
            raise ValueError("__init__ - font '{}' not found.".format(self._font))
        self._size = self._config["size"]
        self._image_font = ImageFont.truetype(self._font, self._size)
        self._string = config["string"]

    def _start(self):
        pass

    def _stop(self):
        pass

    def _update_image(self):
        self._logger.info("StaticText.updateImage()")
        # clear image
        draw = ImageDraw.Draw(self.img)
        draw.rectangle((0, 0, self._width, self._height), fill=self._background_color)
        # write text
        self._logger.info("StaticText.updateImage() - string '{}'.".format(self._string))
        w, h = draw.textsize(self._string, self._image_font)
        x = int((self._width - w) / 2)
        y = int((self._height - h) / 2)
        draw.text((x, y), self._string, font=self._image_font, fill=self._foreground_color)

