from nikippe.renderer.aelementhistory import AElementHistory
from PIL import ImageDraw


class AChart(AElementHistory):
    """
    Abstract class for all chart like graphs. It provides aggregation of incoming asynchronous data points into
    the needed time slots and maintains a history to fill the graph with past data. History length is equivalent to
    displayable data points. Older entries will be purged automatically. Aggregation methods are:
    avg (average), min (minimum), max (maximum), and median.

    additional yaml entries:
            border-top: False
            border-bottom: True
            border-left: True
            border-right: False
            connect-values: True  # if true - values are connected with lines, other wise they are independent dots
            pixel-per-value: 2  # a new value/dot is drawn every n-th pixel on the x-axis. must be > 0.
            range-minimum: 5  # if set, chart minimum value is set to this value. otherwise auto range  (optional)
            range-maximum: 10  # if set, chart maximum value is set to this value. otherwise auto range  (optional)
            history-service:
                ...
    """

    _border_top = None  # boolean
    _border_bottom = None  # boolean
    _border_left = None  # boolean
    _border_right = None  # boolean
    _x1, _y1, _x2, _y2 = [None] * 4  # coordinates for the inner graph - values depend on borders

    _chart_length = None  # number of values to be displayed in the chart
    _chart_height = None  # inner height of chart
    _chart_pixel_per_value = None  # how many pixel from one pixel to the next
    _chart_connect_values = None  # should the value be connected via a line or drawn as dots
    _range_minimum = None  # if set, lower value of chart is limited to _range_minimum
    _range_maximum = None  # if set, upper value of chart is limited to _range_maximum

    def __init__(self, config, update_available, mqtt_client, logger, logger_name):
        """
        Constructor

        :param config: config yaml structure
        :param update_available: Event instance. provided by renderer
        :param mqtt_client: mqtt client instance
        :param logger: logger instance
        :param logger_name: name for spawned logger instance
        """
        AElementHistory.__init__(self, config, update_available, mqtt_client, logger, logger_name)

        self._border_bottom = self._config["border-bottom"]
        self._border_left = self._config["border-left"]
        self._border_right = self._config["border-right"]
        self._border_top = self._config["border-top"]

        self._chart_connect_values = bool(self._config["connect-values"])
        self._chart_pixel_per_value = int(self._config["pixel-per-value"])
        if self._chart_pixel_per_value <= 0:
            self._logger.error("AChart.__init__ - 'pixel-per-value' must be > 0 ('{}').".
                               format(self._chart_pixel_per_value))
            raise ValueError("AChart.__init__ - 'pixel-per-value' must be > 0 ('{}').".
                             format(self._chart_pixel_per_value))
        elif self._chart_pixel_per_value >= self._width:
            self._logger.error("AChart.__init__ - 'pixel-per-value' ({}) must be smaller than the width ({}).".
                               format(self._chart_pixel_per_value, self._width))
            raise ValueError("AChart.__init__ - 'pixel-per-value' ({}) must be smaller than the width ({}).".
                             format(self._chart_pixel_per_value, self._width))

        self._update_margins()
        self._set_max_history_length(self._chart_length)

        try:
            self._range_maximum = self._config["range-maximum"]
        except KeyError:
            pass
        try:
            self._range_minimum = self._config["range-minimum"]
        except KeyError:
            pass

    def _update_margins(self):
        """
        calculate the inner margins and update the corresponding internal values
        """
        self._x1 = 0
        self._y1 = 0
        self._x2 = self._width - 1
        self._y2 = self._height - 1

        if self._border_top:
            self._y1 += 1
        if self._border_right:
            self._x2 -= 1
        if self._border_left:
            self._x1 += 1
        if self._border_bottom:
            self._y2 -= 1

        self._chart_length = int(((self._x2 - self._x1 + 1) / self._chart_pixel_per_value)) + 1
        self._chart_height = self._y2 - self._y1

        self._logger.debug("_update_margins: x1: {}, x2: {}, y1: {}, y2: {}, chart-length: {}, chart-height: {}".
                           format(self._x1, self._x2, self._y1, self._y2, self._chart_length, self._chart_height))


    def _draw_border(self, draw):
        """
        Draw the border according to the config
        :param draw: PIL Image draw instance
        """
        if self._border_top:
            draw.line((0, 0, self._width-1, 0), fill=self._foreground_color, width=1)
        if self._border_right:
            draw.line((self._width - 1, 0, self._width - 1, self._height - 1), fill=self._foreground_color, width=1)
        if self._border_left:
            draw.line((0, 0, 0, self._height-1), fill=self._foreground_color, width=1)
        if self._border_bottom:
            draw.line((0, self._height-1, self._width-1, self._height-1), fill=self._foreground_color, width=1)

    def _update_image(self):
        try:
            with self._history_service.history_lock:
                max_history = self._history_service.history[0]["value"]
                min_history = self._history_service.history[0]["value"]
                for entry in self._history_service.history:
                    max_history = max(entry["value"], max_history)
                    min_history = min(entry["value"], min_history)
        except ValueError:
            max_history, min_history = 0, 0
        except KeyError:
            max_history, min_history = 0, 0
        except IndexError:
            max_history, min_history = 0, 0

        if self._range_maximum is not None:
            max_history = self._range_maximum
        if self._range_minimum is not None:
            min_history = self._range_minimum

        value_range = max_history - min_history
        self._logger.info("AChart.updateImage() - min: {}, max: {}, range: {}, len: {}, height: {}, y2: {}".
                          format(min_history, max_history, value_range, len(self._history_service.history),
                                 self._chart_height, self._y2))
        # clear image
        draw = ImageDraw.Draw(self.img)
        draw.rectangle((0, 0, self._width-1, self._height-1), fill=self._background_color)
        self._draw_border(draw)
        self._update_chartimage(draw, min_history, max_history)
        self._logger.debug("AChart.updateImage - done.")

    def _update_chartimage(self, draw, minimum_value, maximum_value):
        """
        Update image method for silblings of AChart

        :param draw: PIL Image draw instance
        :param minimum_value: minimum value for the chart
        :param maximum_value: maximum value for the chart
        """
        self._logger.error("AChart._update_image - NotImplementedError")
        raise NotImplementedError
