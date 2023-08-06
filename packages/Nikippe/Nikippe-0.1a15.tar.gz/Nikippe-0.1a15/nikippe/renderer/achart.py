from nikippe.renderer.aelementmqtt import AElementMQTT
from PIL import ImageDraw
import time
import collections
import threading


def avg(iterable):
    if len(iterable) == 0:
        return 0
    return sum(iterable)/len(iterable)


def median(iterable):
    if len(iterable) == 0:
        return 0
    pos = int(len(iterable)/2)
    return iterable[pos]


class AChart(AElementMQTT):
    """
    Abstract class for all chart like graphs. It provides aggregation of incoming asynchronous data points into
    the needed time slots and maintains a history to fill the graph with past data. Aggregation methods are:
    avg (average), min (minimum), max (maximum), and median.

    additional yaml entries:
            border-top: False
            border-bottom: True
            border-left: True
            border-right: False
            group-by: 300  # in seconds. 0==no grouping
            aggregator: avg  # aggregator for group-by. valid values: avg, min, max, median. can be omitted
                               if group-by=0.
            connect-values: True  # if true - values are connected with lines, other wise they are independent dots
            pixel-per-value: 2  # a new value/dot is drawn every n-th pixel on the x-axis. must be > 0.
            range-minimum: 5  # if set, chart minimum value is set to this value. otherwise auto range  (optional)
            range-maximum: 10  # if set, chart maximum value is set to this value. otherwise auto range  (optional)
    """

    _history = None  # list of aggregated values. each value represents a time slot with the latest at the last pos.
    _history_lock = None  # Lock - used to lock the history list whenever it is processed or updated
    _aggregation = None  # list of raw values within one time slot
    _aggregator = None  # method to aggregate the values in _aggregation. the result is added to _history
    _group_by = None  # time slot duration in seconds
    _aggregation_timestamp = None  # timestamp for the current aggregation epoch

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
        AElementMQTT.__init__(self, config, update_available, mqtt_client, logger, logger_name)

        self._group_by = int(self._config["group-by"])
        if self._group_by < 0:
            self._logger.error("AChart.__init__ - 'group-by' must be none-negative. ({})".format(self._group_by))
            raise ValueError("AChart.__init__ - 'group-by' must be none-negative. ({})".format(self._group_by))
        try:
            if self._config["aggregator"] == "avg":
                self._aggregator = avg
            elif self._config["aggregator"] == "min":
                self._aggregator = min
            elif self._config["aggregator"] == "max":
                self._aggregator = max
            elif self._config["aggregator"] == "median":
                self._aggregator = median
            else:
                self._logger.error("AChart.__init__ - unknown aggregator '{}'.".format(self._aggregator))
                raise ValueError("AChart.__init__ - unknown aggregator '{}'.".format(self._aggregator))
        except ValueError:
            if self._group_by>0:
                self._logger.error("AChart.__init__ - no aggregator provided. must be set if group-by>0.")
                raise ValueError("AChart.__init__ - no aggregator provided. must be set if group-by>0.")

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

        self._aggregation = []
        self._update_margins()

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

        self._history = collections.deque(maxlen=self._chart_length)
        self._history_lock = threading.Lock()

    def _topic_sub_handler(self, value):
        """
        topic handler - collect all values and as soon as a new aggregation epoch starts move the list to _history
        :param value: incoming value
        """
        value = float(value)
        self._logger.info("AChart._topic_sub_handler - received value '{}'.".format(value))
        t = time.time()
        if self._aggregation_timestamp + self._group_by <= t:  # new epoch - add old value to history/clear aggregation
            self._aggregation_timestamp = t
            self._aggregation_to_history()
        self._aggregation.append(value)

    def _aggregation_to_history(self):
        """
        take all entries in _aggregation, apply _aggregator and add the result to _history.
        """
        aggregation = self._aggregator(self._aggregation)
        with self._history_lock:
            self._history.append(aggregation)
        self._logger.info("AChart._aggregation_to_history - add value: {}, len history: {}".
                  format(aggregation, len(self._history)))
        self._aggregation.clear()
        self._update_available.set()

    def _start(self):
        with self._history_lock:
            self._history.clear()
        self._aggregation.clear()
        self._aggregation_timestamp = time.time()

    def _stop(self):
        self._aggregation_timestamp = None

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
            with self._history_lock:
                max_history = max(self._history)
                min_history = min(self._history)
        except ValueError:
            max_history, min_history = 0, 0

        if self._range_maximum is not None:
            max_history = self._range_maximum
        if self._range_minimum is not None:
            min_history = self._range_minimum

        value_range = max_history - min_history
        self._logger.info("AChart.updateImage() - min: {}, max: {}, range: {}, len: {}, height: {}, y2: {}".
                          format(min_history, max_history, value_range, len(self._history), self._chart_height,
                                 self._y2))
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
