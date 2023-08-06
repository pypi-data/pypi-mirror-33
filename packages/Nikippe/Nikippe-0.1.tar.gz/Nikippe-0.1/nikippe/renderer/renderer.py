from PIL import Image
import threading
import os
from nikippe.renderer.elementfactory import ElementFactory
import pelops.mylogger


class Renderer:
    """
    Renderer controls the single elements and generates an updated image whenever requested. To denote that at least
    one of the elements has received new values an Event (update_available) is used.

    config yaml entries:
        renderer:
            width: 250  # image width
            height: 122  # image height
            background: ../resources/gui_background_2.13.png  # background image - optional
            background-color: 255  # either 0 or 255.
            elements:  # list of elements
                - ...
    """
    _config = None  # config yaml structure
    _logger = None  # logger instance
    _mqtt_client = None  # mqtt client instance

    _elements = None  # list of elements

    _width = None  # width of image
    _height = None  # height of image

    current_image = None  # last generated image
    _base_image = None  # base image - to be used tp generate a new image each time
    _background_image = None  # background image for _base_image - optional

    _lock_update = None  # Lock - needs to be acquired during image update

    update_available = None  # Event - active if at least one of the elements has received new data.

    def __init__(self, config, mqtt_client, logger):
        """
        Constructor

        :param config: config yaml structure
        :param mqtt_client: mqtt client instance
        :param logger: logger instance - a child will be spawned
        """
        self._config = config
        self._logger = pelops.mylogger.get_child(logger, __name__)
        self._logger.info("Renderer.__init__ - creating instance ('{}').".format(config))
        self._mqtt_client = mqtt_client
        self.update_available = threading.Event()
        self._lock_update = threading.Lock()
        self._elements = ElementFactory.create_elements(self._config["elements"],
                                                        self.update_available, self._mqtt_client,
                                                        self._logger)

        self._width = int(self._config["width"])
        self._height = int(self._config["height"])
        self._background_color = int(self._config["background-color"])
        if not 0 <= self._background_color <= 255:
            self._logger.error("Renderer.__init__ - background-color must be in the range 0 - 255 ('{}').".
                             format(self._background_color))
            raise ValueError("Renderer.__init__ - background-color must be in the range 0 - 255 ('{}').".
                             format(self._background_color))

        self._base_image = Image.new('L', (self._width, self._height), self._background_color)
        try:
            self._background_image = Image.open(os.path.expanduser(self._config["background"]))
            self._background_image = self._background_image.convert(mode='L')
            self._base_image.paste(self._background_image, (0,0))
        except KeyError:
            pass  # no background image provided in config file
        self.current_image = self._base_image.copy()

        self._logger.info("Renderer.__init__ - done.")

    def update(self):
        """
        Generates a new image and stores the result in current_image
        """
        self._logger.info("Renderer.update - update renderer ... waiting for lock")
        with self._lock_update:
            self.update_available.clear()
            self._update_elements()
            self.current_image = self._merge_elements_to_new_image()
        self._logger.info("Renderer.update - update renderer ... released lock")

    def _update_elements(self):
        """
        Update each element.
        """
        self._logger.info("Renderer._update_elements - update renderer")
        for element in self._elements:
            try:
                element.update_image()
            except NotImplementedError as e:
                self._logger.error(e)
                raise e

    def _merge_elements_to_new_image(self):
        """
        Merge all elements into base_image at the defined position.
        :return: a PIL image instance
        """
        self._logger.info("Renderer._merge_elements - create new image with the renderer")
        new_image = self._base_image.copy()
        for element in self._elements:
            if element.transparent_background:
                new_image.paste(element.img, (element.x, element.y), element.mask)
            else:
                new_image.paste(element.img, (element.x, element.y))
        return new_image

    def start(self):
        """
        Starts all elements.
        """
        self._logger.info("Renderer.start - starting {} elements.".format(len(self._elements)))
        for e in self._elements:
            try:
                e.start()
            except NotImplementedError as e:
                self._logger.error(e)
                raise e

    def stop(self):
        """
        Stops all elements
        """
        self._logger.info("Renderer.stop - stopping {} elements.".format(len(self._elements)))
        for e in self._elements:
            try:
                e.stop()
            except NotImplementedError as e:
                raise e
