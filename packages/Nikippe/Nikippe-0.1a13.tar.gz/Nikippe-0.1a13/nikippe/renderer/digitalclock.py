from nikippe.renderer.aelement import AElement
from PIL import ImageFont
from PIL import ImageDraw
import time
import os
import os.path


class DigitalClock(AElement):
    """
    Digital clock. provides a new time with every call of update_image. otherwise passive behaviot (no timer
    etc.)

    additional yaml entries:
      font - path to font to be used
      size - font size
    """

    _font = None
    _size = None
    _image_font = None

    def __init__(self, config, update_available, logger):
        AElement.__init__(self, config, update_available, logger, __name__)

        self._font = os.path.expanduser(self._config["font"])
        if not os.path.isfile(self._font):
            self._logger.error("__init__ - font '{}' not found.".format(self._font))
            raise ValueError("__init__ - font '{}' not found.".format(self._font))
        self._size = self._config["size"]
        self._image_font = ImageFont.truetype(self._font, self._size)

    def _start(self):
        pass

    def _stop(self):
        pass

    def _update_image(self):
        self._logger.info("DigitalClock.updateImage()")
        # clear image
        draw = ImageDraw.Draw(self.img)
        draw.rectangle((0, 0, self._width, self._height), fill=self._background_color)
        # write time
        t = time.strftime('%H:%M')
        w, h = draw.textsize(t, self._image_font)
        x = int((self._width - w) / 2)
        y = int((self._height - h) / 2)
        draw.text((x, y), t, font=self._image_font, fill=self._foreground_color)
