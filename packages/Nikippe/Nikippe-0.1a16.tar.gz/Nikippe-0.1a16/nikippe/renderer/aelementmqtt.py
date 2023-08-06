from nikippe.renderer.aelement import AElement


class AElementMQTT(AElement):
    """
    Extension of AElement by mqtt subscription.

    Additional yaml entries
        topic-sub - topic to be subscribed to
    """
    _mqtt_client = None  # mqttclient instance
    _topic_sub = None  # topic to be subscribed to

    def __init__(self, config, update_available, mqtt_client, logger, logger_name):
        """
        Constructor

        :param config: config yaml structure
        :param update_available: Event provided by renderer. can be used to inform renderer of asynchronous updates
        :param mqtt_client: mqtt client instance
        :param logger: logger instance - a child will be spawned
        :param logger_name: name for the spawned logger child
        """
        AElement.__init__(self, config, update_available, logger, logger_name)
        self._mqtt_client = mqtt_client
        self._topic_sub = self._config["topic-sub"]

    def _topic_sub_handler(self, value):
        """abstract - topic handler"""
        self._logger.error("AElementMQTT._topic_sub_handler - NotImplementedError")
        raise NotImplementedError

    def _subscribe(self):
        """subscribe to topic"""
        self._mqtt_client.subscribe(self._topic_sub, self._topic_sub_handler)

    def _unsubscribe(self):
        """unsubscribe from topic"""
        self._mqtt_client.unsubscribe(self._topic_sub, self._topic_sub_handler)

    def start(self):
        """overwritten method from AElement - subscription handling added"""
        AElement.start(self)
        self._subscribe()

    def stop(self):
        """overwritten method from AElement - subscription handling added"""
        AElement.stop(self)
        self._unsubscribe()
