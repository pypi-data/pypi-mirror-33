from nikippe.renderer.achart import AChart


class SequentialChart(AChart):
    """
    Regular chart with the latest values added at the right and the oldest values on the left. If full, the chart is
    shifted to left; the oldest entry removed.

    no additional yaml entries necessary.
    """
    def __init__(self, config, update_available, mqtt_client, logger):
        """
        Constructor

        :param config: config yaml structure
        :param update_available: Event instance. provided by renderer
        :param mqtt_client: mqtt client instance
        :param logger: logger instance
        """
        AChart.__init__(self, config, update_available, mqtt_client, logger, __name__)

    def _update_chartimage(self, draw, minimum_value, maximum_value):
        value_range = maximum_value - minimum_value
        x = self._x1
        last_x = x
        last_y = None
        with self._history_service.history_lock:
            self._logger.info("CircularChart.updateImage() - acquired _history_lock")
            for entry in self._history_service.history:
                value = entry["value"]
                if value is not None:
                    value = min(max(value, minimum_value), maximum_value)
                    int_value = value - minimum_value
                    try:
                        norm_value = int_value / value_range
                    except ZeroDivisionError:
                        norm_value = 0
                    y = self._y2 - int(norm_value * self._chart_height)
                    if self._chart_connect_values:
                        if last_y is None:
                            last_y = y
                        draw.line((last_x, last_y, x, y), fill=self._foreground_color, width=1)
                        last_x, last_y = x, y
                    else:
                        draw.line((x, y, x, y), fill=self._foreground_color, width=1)
                    self._logger.debug(
                        "SequentialChart.updateImage() - draw history. value:{}, dot:@({}/{})".format(value, x, y))
                else:
                    self._logger.debug("SequentialChart.updateImage() - draw history. skipping empty entry (x={})".
                                       format(x))
                x += self._chart_pixel_per_value
        self._logger.info("CircularChart.updateImage() - acquired _history_lock")
