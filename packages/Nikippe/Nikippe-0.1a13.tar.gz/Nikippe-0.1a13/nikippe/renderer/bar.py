from nikippe.renderer.aelementmqtt import AElementMQTT
from enum import Enum
from PIL import ImageDraw


class Orientation(Enum):
    """
    Orientation for bar graph. E.g. if value is UP than the bar will start at the bottom and grow to the top.
    """
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    @classmethod
    def factory(cls, name):
        name = name.lower()
        if name == "up":
            return cls.UP
        elif name == "down":
            return cls.DOWN
        elif name == "left":
            return cls.LEFT
        elif name == "right":
            return cls.RIGHT
        else:
            raise ValueError("Unknown value '{}'.".format(name))


class Bar(AElementMQTT):
    """
    Bar element - displays the current value relative to the configured minimum and maximum values. Orientation
    and borders can be configured.

    additional yaml entries:
            orientation: up  # up, down, left, right
            border: True  # If true, draw a 1 pixel border on all sides with foreground color.
            min-value: 5  # minimum value to be displayed
            max-value: 23  # maximum value to be displayed

    """
    _current_value = None  # last received value
    _min_value = None  # minimum value to be displayed
    _max_value = None  # maximum value to be displayed
    _value_range = None  # max-min
    _draw_border  = None  # if true, draw border
    _orientation = None  # Enum Orientation
    _bar_size = None  # translation of last received value into pixel size

    def __init__(self, config, update_available, mqtt_client, logger):
        """
        Constructor

        :param config: config yaml structure
        :param update_available: Event instance. provided by renderer
        :param mqtt_client: mqtt client instance
        :param logger: logger instance
        """
        AElementMQTT.__init__(self, config, update_available, mqtt_client, logger, __name__)

        self._draw_border = self._config["border"]
        self._orientation = Orientation.factory(self._config["orientation"])
        self._update_bar_size()

        self._max_value = float(self._config["max-value"])
        self._min_value = float(self._config["min-value"])
        self._value_range = self._max_value - self._min_value

        self._current_value = min(self._max_value, max(self._min_value, float(0)))

    def _update_bar_size(self):
        if self._orientation == Orientation.UP or self._orientation == Orientation.DOWN:
            self._bar_size = self._height
        else:
            self._bar_size = self._width
        if self._draw_border:
            self._bar_size = self._bar_size - 2
        if self._bar_size < 1:
            self._logger.error("Bar.__init__ - size of chart must be at least 1 pixel (currently: {}).".
                               format(self._draw_border))
            raise ValueError("Bar.__init__ - size of chart must be at least 1 pixel (currently: {}).".
                             format(self._draw_border))

    def _topic_sub_handler(self, value):
        self._current_value = min(self._max_value, max(self._min_value, float(value)))
        self._logger.info("Bar._topic_sub_handler - received value '{}' -> current value '{}'.".
                          format(value, self._current_value))
        self._update_available.set()

    def _start(self):
        pass

    def _stop(self):
        pass

    def _get_bar_height(self):
        """
        translation of last received value into pixel size for bar
        :return: pixel size for bar
        """
        value = self._current_value - self._min_value
        self._logger.info("Bar._get_bar_height - value: {}, internal value: {}, min: {}, height: {}.".
                          format(self._current_value, value, self._min_value, self._height))
        norm_value = value / self._value_range
        bar_height = int(self._bar_size * norm_value)
        return bar_height

    def _update_image(self):
        bar_height = self._get_bar_height()
        self._logger.info("Bar.updateImage() - value '{}', chart height '{}'".
                          format(self._current_value, bar_height))
        draw = ImageDraw.Draw(self.img)
        draw.rectangle((0, 0, self._width, self._height), fill=self._background_color)
        x1, y1, x2, y2 = 0, 0, self._width-1, self._height-1
        if self._draw_border:
            draw.rectangle((x1, y1, x2, y2), outline=self._foreground_color)
            x1, y1, x2, y2 = x1+1, y1+1, x2-1, y2-1
        if self._orientation == Orientation.UP:
            y1 = y2 - bar_height
        elif self._orientation == Orientation.DOWN:
            y2 = y1 + bar_height
        elif self._orientation == Orientation.LEFT:
            x1 = x2 - bar_height
        elif self._orientation == Orientation.RIGHT:
            x2 = x1 + bar_height
        else:
            self._logger.error("Bar.update_image - don't know how to handle orientation enum '{}'".
                               format(self._orientation))
            raise ValueError("Bar.update_image - don't know how to handle orientation enum '{}'".
                             format(self._orientation))
        self._logger.info("Bar.updateImage() - rectangle({}, {}, {}, {}).".
                          format(x1, y1, x2, y2))
        draw.rectangle((x1, y1, x2, y2), fill=self._foreground_color)



