import os
from nikippe.renderer.aelementmqtt import AElementMQTT
from PIL import Image, ImageChops


class ImageList(AElementMQTT):
    """
    Image list preloads a set of images and displays one based on received mqtt-messages.

    additional yaml entries:
      default-image - name of image to be displayed before any message has been received
      images
        - name - name for this image - if this name is received on topic-sub, this image will be displayed
          image - path to image to be used
          offset_x - offset for image within element plane (optional, default=0)
          offset_y - offset for image within element plane (optional, default=0)
        - ...
    """
    _images = None  # dict for images
    _selected_image = None  # pointer to the one image from images, that should be displayed

    def __init__(self, config, update_available, mqtt_client, logger):
        AElementMQTT.__init__(self, config, update_available, mqtt_client, logger, __name__)

        self._images = {}
        for c in self._config["images"]:
            name = c["name"].lower()
            image = Image.open(os.path.expanduser(c["image"]))
            try:
                offset_x = c["offset_x"]
            except KeyError:
                offset_x = 0
            try:
                offset_y = c["offset_y"]
            except KeyError:
                offset_y = 0
            self._images[name] = {
                "image": image,
                "offset_x": offset_x,
                "offset_y": offset_y
            }
            self._logger.debug("added image '{}:{}'".format(name, self._images[name]))
        self._set_selected_image(self._config["default-image"].lower())

    def _set_selected_image(self, name):
        try:
            self._selected_image = self._images[name]
        except KeyError as e:
            self._logger.error("ImageList._set_selected_image - no image named '{}' found in image list '{}'.".
                               format(name, self._images.keys()))
            raise e
        self._logger.info("ImageList._set_selected_image - set to image with name '{}'.".format(name))

    def _topic_sub_handler(self, value):
        value = value.decode("utf-8")
        self._logger.info("ImageList._topic_sub_handler - received value '{}'.".format(value))
        self._set_selected_image(str(value.lower()))
        self._update_available.set()

    def _start(self):
        pass

    def _stop(self):
        pass

    def _update_image(self):
        self._logger.info("ImageList.updateImage()")
        # clear result image
        self.img = ImageChops.constant(self.img, self._background_color)
        # place static image
        self.img.paste(self._selected_image["image"],
                       box=(self._selected_image["offset_x"],
                            self._selected_image["offset_y"]))

