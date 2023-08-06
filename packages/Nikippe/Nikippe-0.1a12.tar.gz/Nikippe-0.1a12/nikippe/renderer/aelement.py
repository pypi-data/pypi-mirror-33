from PIL import Image, ImageChops, ImageMath
import pelops.mylogger


class AElement:
    """
    AElement is the base class for all elements that can be rendered to one image.

    yaml base config for each element consists of the following entries:
        name - unique name for the element
        type - type of element
        active - if set to false, entry will be ignored by entryfactory
        x - x offset
        y - y offset
        width - width
        height - height
        foreground-color - either 0 or 255.
        background-color - either 0 or 255.
        transparent-background - boolean (optional)
    """

    _config = None  # config yaml structure
    _logger = None  # logger instance
    name = None  # name of element

    img = None  # image
    _width = None  # width of image
    _height = None  # height of image
    x = None  # x offset of image - to be used by renderer to stich the elements together
    y = None  # y offset of image - to be used by renderer to stich the elements together

    _foreground_color = None  # foreground color
    _background_color = None  # background color
    transparent_background = None  # boolean - if True, alpha channel is set with background color
    _img_comparator = None  # image with the same size as img and with background color
    mask = None  # image mask based on background-color - generated only if transparent_background = True

    _update_available = None  # Event instance

    def __init__(self, config, update_available, logger, logger_name):
        """
        Constructor

        :param config: config yaml structure
        :param update_available: Event provided by renderer. can be used to inform renderer of asynchronous updates
        :param logger: logger instance - a child will be spawned
        :param logger_name: name for the spawned logger child
        """
        self._config = config
        self._logger = pelops.mylogger.get_child(logger, logger_name)

        self._update_available = update_available
        self._logger.info("{}.__init__ - creating instance.".format(self.__class__.__name__))
        self._logger.debug("{}.__init__ - config:".format(config))
        if not self.__class__.__name__.lower() == self._config["type"].lower():
            self._logger.error("type '{}' as given in config is not equvivalent to class type '{}'.".
                                format(self._config["type"].lower(), self.__class__.__name__.lower()))
            raise ValueError("type '{}' as given in config is not equvivalent to class type '{}'.".
                             format(self._config["type"].lower(), self.__class__.__name__.lower()))
        self.name = self._config["name"]

        self._width = int(self._config["width"])
        self._height = int(self._config["height"])
        self.x = int(self._config["x"])
        self.y = int(self._config["y"])
        self._foreground_color = int(self._config["foreground-color"])
        self._background_color = int(self._config["background-color"])
        try:
            self.transparent_background = bool(self._config["transparent-background"])
        except KeyError:
            self.transparent_background = False

        if not 0 <= self._foreground_color <= 255:
            self._logger.error("AElement.'{}' - foreground-color must be in the range of 0 - 255 ('{}').".
                               format(self.name, self._foreground_color))
            raise ValueError("AElement.'{}' - foreground-color must be in the range of 0 - 255 ('{}').".
                             format(self.name, self._foreground_color))
        if not 0 <= self._background_color <= 255:
            self._logger.error("AElement.'{}' - background-color must be in the range of 0 - 255 ('{}').".
                               format(self.name, self._background_color))
            raise ValueError("AElement.'{}' - background-color must be in the range of 0 - 255 ('{}').".
                             format(self.name, self._background_color))

        self.img = Image.new('L', (self._width, self._height), self._background_color)
        self.mask = Image.new('L', (self._width, self._height), 255)
        self._transparent_comparator = Image.new('L', (self._width, self._height), self._background_color)

    def start(self):
        """start the element"""
        self._logger.info("starting")
        self._start()

    def _start(self):
        """abstract"""
        self._logger.error("AElement._start - NotImplementedError")
        raise NotImplementedError

    def stop(self):
        """stop the element"""
        self._stop()
        self._logger.info("stopped")

    def _stop(self):
        """abstract"""
        self._logger.error("AElement._stop - NotImplementedError")
        raise NotImplementedError

    def update_image(self):
        self._update_image()
        if self.transparent_background:
            # mask must have 0 for each transparent pixel and 255 for each non-transparent one.
            # ImageChops.difference satisfies the first demand
            # ImageMath a*255 satisfies the second demand
            temp = ImageChops.difference(self.img, self._transparent_comparator)
            self.mask = ImageMath.eval("convert(a*255, 'L')", a=temp)

    def _update_image(self):
        """abstract - called by renderer to request a new image from the element"""
        self._logger.error("AElement.update_image - NotImplementedError")
        raise NotImplementedError
