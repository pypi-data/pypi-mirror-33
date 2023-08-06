from nikippe.renderer.aelementmqtt import AElementMQTT
from pelops.historyservice import HistoryService


class AElementHistory(AElementMQTT):
    """
    additional yaml entries:
            history-service:
                group-by: 300  # in seconds. must be > 0.
                aggregator: avg  # aggregator for group-by. valid values: avg, min, max, median. can be omitted
                                   if group-by=0.
                use-dataservice: True  # use the dataservice archippe to fill the chart with persisted data
                dataservice-request-topic-prefix: /dataservice/request
                dataservice-response-topic-prefix: /dataservice/response
    """

    _history_service =None

    def __init__(self, config, update_available, mqtt_client, logger, logger_name):
        """
        Constructor

        :param config: config yaml structure
        :param update_available: Event provided by renderer. can be used to inform renderer of asynchronous updates
        :param mqtt_client: mqtt client instance
        :param logger: logger instance - a child will be spawned
        :param logger_name: name for the spawned logger child
        """
        AElementMQTT.__init__(self, config, update_available, mqtt_client, logger, logger_name)

        self._history_service = HistoryService(self._config["history-service"], None, self._topic_sub, False,
                                               self._update_available, self._mqtt_client, self._logger)

    def _set_max_history_length(self, max_length):
        self._history_service.set_max_length(max_length)

    def _topic_sub_handler(self, value):
        """
        topic handler - collect all values and as soon as a new aggregation epoch starts move the list to _history
        :param value: incoming value
        """
        value = float(value)
        self._logger.info("AChart._topic_sub_handler - received value '{}'.".format(value))
        self._history_service.add_value(value)

    def _start(self):
        self._history_service.start()

    def _stop(self):
        self._history_service.stop()