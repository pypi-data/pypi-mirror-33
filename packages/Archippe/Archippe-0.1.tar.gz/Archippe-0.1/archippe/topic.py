from pelops.mylogger import get_child
from pelops.myinfluxdbclient import MyInfluxDBClient
import datetime
import json


class Topic:
    """
    Topic handles storage and retrieval for the given mqtt-topic. It registers to topic_request and expect two different
    types of messages:
      * timespan in seconds to be substracted from now(). float value.
      * timestamps "from" and "to" and "group-by" in secons in a json structure. e.g. ```{"from":
        "2009-11-10T22:00:00Z", "to": "2009-11-10T23:00:00Z", "group-by": 60}``` (timestamp are
        inclusive: "where t<=to and t>=from"; group-by must be integer)

    The resulting list of timestamp/value pairs is published to topic_publish.
    """

    _mqtt_client = None  # mqtt client instance
    _topic_sub = None  # topic of interest
    _topic_response = None  # publish historic data
    _topic_request = None  # listen to data requests
    _influxdb = None  # influxdb client instance
    _time_format = "%Y-%m-%dT%H:%M:%S.%fZ"  # time format string for influxdb queries
    _conversion = None  # conversion method - used to convert the incoming message

    def __init__(self, topic_sub, topic_request, topic_response, conversion, mqtt_client, logger, influxdb):
        """
        Constructor

        :param topic_sub: mqtt-topic - topic of interest
        :param topic_request: mqtt-topic - listen to data requests
        :param topic_response: mqtt-topic - publish results
        :param mqtt_client: mqtt client instance
        :param logger: logger instance
        :param influxdb: influxdb client instance
        """

        self._influxdb = influxdb
        self._mqtt_client = mqtt_client
        self._topic_sub = topic_sub
        self._topic_request = topic_request
        self._topic_response = topic_response
        self._conversion = conversion
        self._logger = get_child(logger, __name__ + "." + self._topic_sub)
        self._logger.info("Topic.__init__ - initializing")
        self._logger.debug("Topic.__init__ - sub: {}, request: {}, reponse: {}, measurement: {}, conversion: {}.".
                           format(self._topic_sub, self._topic_request, self._topic_response,
                                  MyInfluxDBClient.escape_name(self._topic_sub), self._conversion))

    def _handler_sub(self, value):
        """
        Receive values publish to the topic of interest and store store them in influxdb.
        :param value: raw value
        """
        value = self._conversion(value)
        self._logger.info("received value {} on topic {}.".format(value, self._topic_sub))
        self._influxdb.write_point(self._topic_sub, value)

    def _handler_request(self, message):
        """
        Processes historic data requests and publishes the result to topic_response.
        :param message: Request received via topic_request. Either float value or json structur (to, from, group-by).
        """
        timestamp_from, timestamp_to, group_by = self._extract_parameters(message)
        if timestamp_to is None or timestamp_from is None:
            self._logger.error("_handler_request - received malformed message '{}' on topic '{}'.".
                               format(message, self._topic_request))
        else:
            history = list((self._fetch_history(timestamp_from, timestamp_to, group_by)).get_points())
            self._logger.info("_handler_request - publishing list with {} values.".format(len(history)))
            self._mqtt_client.publish(self._topic_response, json.dumps(history))

    def _fetch_history(self, timestamp_from, timestamp_to, group_by):
        """
        Fetch data from influxdb in the timerange: from<=t and to<=t. Optionally apply group_by.
        :param timestamp_from: datetime timestamp
        :param timestamp_to: datetime timestamp
        :param group_by: group_by float value or None
        :return: list with measurements
        """
        self._logger.info("_fetch_history: topic '{}', from '{}', to '{}', group-by '{}'.".
                          format(self._topic_sub, timestamp_from, timestamp_to, group_by))
        timestamp_to = timestamp_to.strftime(self._time_format)
        timestamp_from = timestamp_from.strftime(self._time_format)
        measurement = MyInfluxDBClient.escape_name(self._topic_sub)

        if group_by is None:
            query = 'select value as value from "{}" where time <= \'{}\' and time >= \'{}\''.\
                format(measurement, timestamp_to, timestamp_from)
        else:
            query = 'select mean(value) as value from "{}" where time <= \'{}\' and time >= \'{}\' group by time({}s)'. \
                format(measurement, timestamp_to, timestamp_from, group_by)

        self._logger.debug("_fetch_history - query: '{}'.".format(query))
        history = self._influxdb.client.query(query)

        self._logger.debug("_fetch_history - query result: '{}'.".format(history))

        return history

    def _extract_parameters(self, message):
        """
        Extract the parameters to, from, and group-by from the message.

        :param message: Message can either be float of a json structure (to, from, group-by)
        :return: timestamp_from, timestamp_to, group_by - timestamps are datetime objects and group_by is float
        """
        timestamp_to = None
        timestamp_from = None
        group_by = None

        try:
            timestamp_from = datetime.datetime.now() - datetime.timedelta(seconds=float(message))
            timestamp_to = datetime.datetime.now()
        except ValueError:
            message = message.decode("utf-8")
            message = json.loads(message)
            try:
                timestamp_from = datetime.datetime.strptime(message["from"], self._time_format)
            except KeyError:
                self._logger.error("_extract_parameters - key 'from' not found.")
            try:
                timestamp_to = datetime.datetime.strptime(message["to"], self._time_format)
            except KeyError:
                self._logger.error("_extract_parameters - key 'to' not found.")
            try:
                group_by = int(message["group-by"])
            except KeyError:
                self._logger.info("_extract_parameters - optional key 'group-by' not found.")
            except ValueError:
                self._logger.error("_extract_parameters - type of entry 'group-by' is not int - parameter ignored")

        return timestamp_from, timestamp_to, group_by

    def start(self):
        """Subscribe topics."""
        self._mqtt_client.subscribe(self._topic_sub, self._handler_sub)
        self._mqtt_client.subscribe(self._topic_request, self._handler_request)
        self._logger.info("started")

    def stop(self):
        """Unsubscribe topics."""
        self._mqtt_client.unsubscribe(self._topic_sub, self._handler_sub)
        self._mqtt_client.unsubscribe(self._topic_request, self._handler_request)
        self._logger.info("stopped")
