from nikippe.renderer.achart import AChart
from enum import Enum
from datetime import datetime, timedelta
import copy


class TimeSpan (Enum):
    """
    Each enum entry is a method with parameter "now" and takes a datetime instance. It returns two datetime instances
    first and last. They represent the time span the provided datetime value belongs to. For example, if you call
    TimeSpan.WEEK(datetime('weekday'=1))* you will get first.weekday=0 and last.weekday=6 surrounding this datetime.

    * pseudo code
    """

    def WEEK(now):
        """Monday-Sunday"""
        first = copy.deepcopy(now)
        first = first.replace(hour=0, minute=0, second=0, microsecond=0)
        first = first + timedelta(days=-now.weekday())
        last = first + timedelta(weeks=1)
        return first, last

    def DAY(now):
        """0h-24h"""
        first = copy.deepcopy(now)
        first = first.replace(hour=0, minute=0, second=0, microsecond=0)
        last = first + timedelta(days=1)
        return first, last

    def HOUR(now):
        """:00m-:60m"""
        first = copy.deepcopy(now)
        first = first.replace(minute=0, second=0, microsecond=0)
        last = first + timedelta(hours=1)
        return first, last

    def MINUTE(now):
        """:00s-60s"""
        first = copy.deepcopy(now)
        first = first.replace(second=0, microsecond=0)
        last = first + timedelta(minutes=1)
        return first, last

    @classmethod
    def get_enum(cls, name):
        """
        Factory-method
        :param name: String
        :return: TimeSpan enum
        """
        name = name.upper()
        if name == cls.WEEK.__name__:
            return cls.WEEK
        elif name == cls.DAY.__name__:
            return cls.DAY
        elif name == cls.HOUR.__name__:
            return cls.HOUR
        elif name == cls.MINUTE.__name__:
            return cls.MINUTE
        else:
            raise ValueError("unkown value '{}'".format(name))


class CircularChart(AChart):
    """
    A circular chart with a static time axis (e.g 00:00-23:59). Usefull e.g. if value changes from yesterday should be
    compared to todays values for each time slot. New Values are placed at the corresponding position on the x axis
    (and old ones overwritten). Thus, old values do not "drop out" at the left (see sequential chart); they are at
    the same position and until they are overwritten.

    Possible time spans for the static time axis are:
        - Week: Monday to Sunday (Days)
        - Day: 00:00 to 24:00 (Hours)
        - Hour: :00 to :60 (Minutes)
        - Minute: ::00 to ::60 (Seconds)

    additional yaml entries:
        draw-cursor: True  # draw a cursor at the current time slot
        time-span: Day  # Week, Day, Hour, Minute
    """

    _display_cursor = None  # draw a cursor at the current time slot
    _time_span = None  # TimeSpan enum value

    def __init__(self, config, update_available, mqtt_client, logger):
        """
        Constructor

        :param config: config yaml structure
        :param update_available: Event instance. provided by renderer
        :param mqtt_client: mqtt client instance
        :param logger: logger instance
        """
        AChart.__init__(self, config, update_available, mqtt_client, logger, __name__)

        self._display_cursor = bool(self._config["draw-cursor"])
        try:
            self._time_span = TimeSpan.get_enum(self._config["time-span"])
        except ValueError as e:
            self._logger.error("__init__ - TimeSpan ValueError: {}".format(e))
            raise ValueError("__init__ - TimeSpan ValueError: {}".format(e))

    def _get_timeslot_shift(self):
        """
        Calculates the factor of time passed in the general time slot. For example, if TimeSlot.Day is selected and
        current time is 12:00:00, the result is 0.5.

        :return: float [0,1] - percentage of time passed in current TimeSlot.
        """
        now = datetime.now()
        first, last = self._time_span(now)

        if now < first:
            self._logger.error("_get_timeslot_shift - now ({}) must be >= first ({})".format(now, first))
            raise ValueError("_get_timeslot_shift - now ({}) must be >= first ({})".format(now, first))

        if now >= last:
            self._logger.error("_get_timeslot_shift - now ({}) must be < last ({})".format(now, last))
            raise ValueError("_get_timeslot_shift - now ({}) must be < last ({})".format(now, last))

        range = last - first
        range_pos = now - first
        factor = range_pos / range

        self._logger.info("_get_timeslot_shift - first: {}, now: {}, last: {}, factor: {}".
                          format(first, now, last, factor))
        return factor

    def _get_timed_data(self, minimum_value, maximum_value):
        """
        A circular chart jas a fixed set of vaiable to be displayed. New Values overwrite the old one from the same
        relative time in the previous time slot.

        Example:
            - incoming values are (oldest first): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
            19, 20, 21, 22, 23, 24, 25, 26]
            - current time is 03:00:00
            - resulting list should bef: [23, 24, 25, 26, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
            19, 20, 21, 22]

        :param minimum_value: min range or autorange if None
        :param maximum_value:  max range or autorange if None
        :return: list of normalized data in the correct order
        """
        value_range = maximum_value - minimum_value
        data = [None] * self._chart_length

        with self._history_service.history_lock:
            self._logger.info("_get_timed_data - acquired _history_lock")
            pos = self._chart_length - len(self._history_service.history) # if queue is not fully filled, increase start value accordingly
            pos_shift = int(self._chart_length * (1-self._get_timeslot_shift()))
            self._logger.debug("_get_timed_data - startpos: {}, pos shift: {}".format(pos, pos_shift))
            for entry in self._history_service.history:
                value = entry["value"]
                if value is not None:
                    value = min(max(value, minimum_value), maximum_value)
                    int_value = value - minimum_value
                    try:
                        norm_value = int_value / value_range
                    except ZeroDivisionError:
                        norm_value = None
                else:
                    norm_value = None
                timeslot = (pos - pos_shift) % self._chart_length
                data[timeslot] = norm_value
                self._logger.debug("_get_timed_data() - added value:{} / norm_value:{}, @{}".
                                   format(value, norm_value, timeslot))
                pos = pos + 1
        self._logger.info("_get_timed_data() - released _history_lock")
        return data

    def _draw_values(self, draw, data):
        """
        Draws the chart for the provided list of normalized values.

        :param draw: instance of ImageDraw of the target Image.
        :param data: list of values
        """
        x = self._x1
        last_x = x
        last_y = None

        self._logger.info("_draw_values()")
        count = 0
        for norm_value in data:
            if norm_value is not None:
                y = self._y2 - int(norm_value * self._chart_height)
                self._logger.debug("_draw_values() - value:{}, dot:@({}/{})".format(norm_value, x, y))
                if self._chart_connect_values:
                    if last_y is None:
                        last_y = y
                    draw.line((last_x, last_y, x, y), fill=self._foreground_color, width=1)
                    last_x, last_y = x, y
                else:
                    draw.line((x, y, x, y), fill=self._foreground_color, width=1)
            else:
                self._logger.info("CircularChart._draw_values - {}. entry is None.".format(count))
            count = count + 1
            x += self._chart_pixel_per_value

    def _draw_cursor(self, draw):
        """
        Draws a vertical block at the current time slot. For example, if a time slot is 15 minutes and it is
        12:13 then the are from 12:00 until 12:14:59 is painted in foreground color.

        :param draw: instance of ImageDraw of the target Image.
        """
        pos = int(self._chart_length * self._get_timeslot_shift())
        x1 = self._x1 + pos * self._chart_pixel_per_value
        x2 = x1 + self._chart_pixel_per_value

        self._logger.info("_draw_cursor - pos:{}, x1:{}, y1:{}, x2:{}, y2:{}".format(pos, x1, self._y1, x2, self._y2))
        draw.rectangle([x1, self._y1, x2, self._y2], fill=self._foreground_color)

    def _update_chartimage(self, draw, minimum_value, maximum_value):
        data = self._get_timed_data(minimum_value, maximum_value)
        self._draw_values(draw, data)
        if self._display_cursor:
            self._draw_cursor(draw)
