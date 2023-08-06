import nikippe
import time
import threading
from io import BytesIO
from nikippe.renderer.renderer import Renderer
from pelops.abstractmicroservice import AbstractMicroservice
from nikippe.schema.displayserver import get_schema


class DisplayServer(AbstractMicroservice):
    """
    Main class of display-server. It is responsible for starting and distributing the updates. Updates happen either
    timer/interval based and/or if active elements (e.g. receives new values via mqtt) are "updateable". The resulting
    image is published.

    Note: The event _update_available will be called upon stopping a last time. Make sure to check if _stop_service is
    not set when using this event.

    Config yaml:
        display-server:
            topics-pub-image: /test/image  # send image to the display driver
            send-on-change: True  # send new image to epaper if any element reports that it received an update
            send-interval: 60  # seconds. if 0 interval is disabled.
            renderer:
                    ...
    """
    _version = nikippe.version  #versionof the software

    _lock_update = None  # Lock used to ensure that update is called while the last call of update is still in working

    _renderer = None  # instance of nikippe.renderer.renderer - integrates all elements into one image

    _send_interval = None  # update and send the image every n seconds
    _activate_loop = None  # booelan - if True a loop thread is created
    _last_timestamp = None  # timestamp of last updated and sent image
    _loop_thread = None  # thread for method DisplayServer._poll_loop

    _send_on_change = None  # boolean - if True the image is updated and send as soon as an element has an update
    _update_available = None  # event that triggers as soon as one of the elements has an update available
    _update_thread = None  # thread for method DisplayServer._update_available_detection

    _topics_pub_image = None  # publish the encoded image to this topic

    def __init__(self, config, mqtt_client=None, logger=None):
        """
        Constructor

        :param config: config yaml structure
        :param mqtt_client: instance of the mqtt client (optional)
        :param logger: instance of logger (optional)
        """
        AbstractMicroservice.__init__(self, config, "display-server", mqtt_client, logger, __name__)

        self._renderer = Renderer(self._config["renderer"], self._mqtt_client, self._logger)

        self._set_send_interval(int(self._config["send-interval"]))
        self._set_on_change(bool(self._config["send-on-change"]))
        self._topics_pub_image = self._config["topics-pub-image"]

        self._lock_update = threading.Lock()

        self._logger.info("DisplayServer.__init__ - done.")

    def _set_send_interval(self, interval):
        self._logger.info("DisplayServer._set_send_interval - setting send interval to '{}'.".format(interval))
        self._send_interval = interval
        if self._send_interval < 0:
            self._logger.error("DisplayServer.__init__ - send-interval must be >=0 (currently {}).".
                               format(self._send_interval))
            raise ValueError("DisplayServer.__init__ - send-interval must be >=0 (currently {}).".
                             format(self._send_interval))
        if self._send_interval == 0:
            self._activate_loop = False
        else:
            self._activate_loop = True
        self._loop_thread = threading.Thread(target=self._poll_loop)

    def _set_on_change(self, on_change):
        """
        Prepares the thread for _update_available_detection
        :param on_change: boolean - if false, update events are ignored
        """
        self._logger.info("DisplayServer._set_on_change - set value to '{}'.".format(on_change))
        self._send_on_change = on_change
        self._update_available = self._renderer.update_available
        self._update_thread = threading.Thread(target=self._update_available_detection)

    def _update_available_detection(self):
        """
        Waits for _update_available events - will be stopped by self._stop
        """
        self._logger.info("DisplayServer._update_available_detection - wait for updates.")

        while not self._stop_service.isSet():
            if self._update_available.wait():
                if not self._stop_service.isSet():
                    self._update()

    def _calc_sleep_time(self):
        """
        Calculates the time to the end of the current interval. This reduces jitter and drift - ensures that updates
        are sent every nth second.
        :return: seconds (float) until next interval.
        """
        current_time = time.time()
        next_timestamp = self._last_timestamp + self._send_interval
        sleep_time = next_timestamp - current_time
        self._logger.info("DisplayServer._calc_sleep_time - seconds to next interval: '{} s' ({}).".
                          format(sleep_time, current_time))
        return sleep_time

    def _poll_loop(self):
        """
        Calls update every nth second.
        """
        self._logger.info("DisplayServer._poll_loop - entered poll_loop method.")

        self._last_timestamp = time.time()

        while not self._stop_service.isSet():
            print("update DisplayServer @ {}.".format(time.time()))
            self._update()
            sleep_for = self._calc_sleep_time()
            self._logger.info("DisplayServer._poll_loop - sleep for " + str(sleep_for) + " seconds.")
            self._stop_service.wait(sleep_for)
            self._last_timestamp = time.time()

        self._logger.info("DisplayServer._poll_loop - exiting poll_loop method.")

    def _update(self):
        """
        Collects latest version of image from renderer and publishes it to _topics_pub_image.
        :return:
        """
        self._logger.info("DisplayServer._update - getting new image and publishing it")
        with self._lock_update:
            self._renderer.update()
            img = self._renderer.current_image
            msg = self._to_full_image_message(img)
            self._mqtt_client.publish(self._topics_pub_image, msg)
        self._logger.info("DisplayServer._update - done")

    def _to_full_image_message(self, image):
        """Convert a PIL.Image instance to bytes - the format needed if the mqtt payload consists of only the image."""
        bytes_image = BytesIO()
        image.save(bytes_image, format="png")
        result = bytes_image.getvalue()
        return result

    def _start(self):
        """
        starts renderer and optionally starts polling and/or update-event based image updates.
        """
        self._renderer.start()

        if self._activate_loop:
            self._logger.info("DisplayServer.start - activate loop")
            self._loop_thread.start()
        if self._send_on_change:
            self._logger.info("DisplayServer.start - activate on-update")
            self._update_thread.start()

    def _stop(self):
        """
        stops renderer and polling/update threads. sends _updae_available event for this purpose.
        """
        if self._activate_loop:
            self._loop_thread.join()
        if self._send_on_change:
            if self._stop_service.isSet():
                # fire this event to stop the thread _update_available_detection. but only if stop_service is set
                self._update_available.set()
            else:
                self._logger.error("DisplayServer._stop - _stop_service must be set.")
                raise RuntimeError("DisplayServer._stop - _stop_service must be set.")
            self._update_thread.join()
        self._renderer.stop()

    @classmethod
    def _get_description(cls):
        return "General purpose display server."

    @classmethod
    def _get_schema(cls):
        return get_schema()


def standalone():
    DisplayServer.standalone()


if __name__ == "__main__":
    DisplayServer.standalone()
