from pelops.abstractmicroservice import AbstractMicroservice
from pelops.myinfluxdbclient import MyInfluxDBClient
from archippe.topic import Topic
from archippe.schema import get_schema


class DataPersistence(AbstractMicroservice):
    """
    The main entry point for the data persistence service. Creates the Topic-instances and starts/stops them.

    Yaml config:
    data-persistence:
        topics:  # list of topics that should be persisted
            - topic: /test/temperature
              type: float  # float, integer, string, boolean
            - topic: /test/humidity
              type: float  # float, integer, string, boolean
        topic-request-prefix: /dataservice/request  # prefix for each topic to request historic data
        topic-response-prefix: /dataservice/response  # prefix for each topic to publish historic data

    """
    _influx_client = None
    _topics = None

    def __init__(self, config, mqtt_client=None, logger=None):
        """
        Constructor.

        :param config: config yaml structure
        :param mqtt_client: instance of an mqtt client (optional)
        :param logger: instance of a logger (optional)
        """

        AbstractMicroservice.__init__(self, config, "data-persistence", mqtt_client=mqtt_client, logger=logger,
                                      logger_name=__name__)
        self._influx_client = MyInfluxDBClient(config["influx"], self._logger)

        prefix_request = self._config["topic-request-prefix"]
        prefix_response = self._config["topic-response-prefix"]

        self._topics = []
        for c in self._config["topics"]:
            topic_sub = c["topic"]

            if c["type"].lower() == "integer":
                conversion = int
            elif c["type"].lower() == "float":
                conversion = float
            elif c["type"].lower() == "boolean":
                conversion = bool
            elif c["type"].lower() == "string":
                conversion = str
            else:
                self._logger.error("Unkown type '{}'.".format(c["type"]))
                raise ValueError("Unkown type '{}'.".format(c["type"]))

            topic = Topic(topic_sub, prefix_request+topic_sub, prefix_response+topic_sub, conversion, self._mqtt_client,
                          self._logger, self._influx_client)
            self._topics.append(topic)

    def _start(self):
        for topic in self._topics:
            topic.start()

    def _stop(self):
        for topic in self._topics:
            topic.stop()

    @classmethod
    def _get_schema(cls):
        return get_schema()

    @classmethod
    def _get_description(cls):
        return "Archippe is a data persistence micro service for pelops. It uses influxdb to store incoming values " \
               "and publishes the history a series upon request."


def standalone():
    """Calls the static method DataPersistence.standalone()."""
    DataPersistence.standalone()


if __name__ == "__main__":
    DataPersistence.standalone()
