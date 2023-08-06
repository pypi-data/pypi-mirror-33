import os
from nikippe.renderer.aelement import AElement
from PIL import Image, ImageChops


class StaticImage(AElement):
    """
    Displays a static image.

    additional yaml entries:
      image - path to image to be used
      offset_x - offset for image within element plane (optional, default=0)
      offset_y - offset for image within element plane (optional, default=0)
    """
    _static_image = None
    _offset_x = None
    _offset_y = None

    def __init__(self, config, update_available, logger):
        AElement.__init__(self, config, update_available, logger, __name__)

        self._static_image = Image.open(os.path.expanduser(self._config["image"]))
        self._static_image = self._static_image.convert(mode="L")
        try:
            self._offset_x = self._config["offset_x"]
        except KeyError:
            self._offset_x = 0
        try:
            self._offset_y = self._config["offset_y"]
        except KeyError:
            self._offset_y = 0

    def _start(self):
        pass

    def _stop(self):
        pass

    def _update_image(self):
        self._logger.info("StaticImage.updateImage()")
        # clear result image
        self.img = ImageChops.constant(self.img, self._background_color)
        # place static image
        self.img.paste(self._static_image, box=(self._offset_x, self._offset_y))

