from nikippe.renderer.aelement import AElement
from PIL import ImageFont
from PIL import ImageDraw
import time
import os
import os.path
import threading
from datetime import datetime


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
    _timer = None  # thread that operates _full_minute_timeout
    _stop_timer = None  # event stop full_minute_timeout

    def __init__(self, config, update_available, logger):
        AElement.__init__(self, config, update_available, logger, __name__)

        self._font = os.path.expanduser(self._config["font"])
        if not os.path.isfile(self._font):
            self._logger.error("__init__ - font '{}' not found.".format(self._font))
            raise ValueError("__init__ - font '{}' not found.".format(self._font))
        self._size = self._config["size"]
        self._image_font = ImageFont.truetype(self._font, self._size)
        self._stop_timer = threading.Event()
        self._timer = threading.Thread(target=self._full_minute_timeout)

    def _full_minute_timeout(self):
        """
        Waits until the next minute has started and sends an _update_available event. 0.01 seconds are added to the
        waiting time to ensure that the new epoch has really started (jitter, ...). Might be unnecessary but this
        safety in costs 1/6000 of one interval -> neglectable.
        Runs until _stop_timer event is set.
        e.g. 23:43:15.7 will wait 44.31 seconds
        """
        guarantee_delay = 0.01  # "guarantees" that it is already the next minute
        self._logger.info("DigitalClock._full_minute_timeout started")
        while not self._stop_timer.isSet():
            current = datetime.now()
            next_full_minute_in = 60 - (current.second + current.microsecond/1000000)
            next_full_minute_in = next_full_minute_in + guarantee_delay
            self._logger.debug("DigitalClock._full_minute_timout - current {}s, wait {}s.".
                               format(current, next_full_minute_in))
            self._stop_timer.wait(next_full_minute_in)
            self._update_available.set()
        self._logger.info("DigitalClock._full_minute_timeout stopped")

    def _start(self):
        self._stop_timer.clear()
        self._timer.start()

    def _stop(self):
        self._stop_timer.set()
        self._timer.join()

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
