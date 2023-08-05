import unittest
import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops.read_config import read_config, validate_config
from archippe.topic import Topic
from pelops.myinfluxdbclient import MyInfluxDBClient
from pelops.mylogger import create_logger
from pelops.mqttclient import MQTTClient
from threading import Event
import json
import datetime


# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', msg=None):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    if msg is None:
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    else:
        print('\r%s |%s| %s%% %s %s' % (prefix, bar, percent, suffix, msg), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


class TestValidateConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = read_config(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) +
                                 "/tests_unit/config.yaml")
        cls.logger = create_logger(cls.config["logger"], "TestValidateConfig")
        cls.logger.info("start")
        cls.mqtt_client = MQTTClient(cls.config["mqtt"], cls.logger)
        cls.mqtt_client.connect()
        cls.influxdb = MyInfluxDBClient(cls.config["influx"], cls.logger)

    @classmethod
    def tearDownClass(cls):
        cls.influxdb.client.close()
        cls.mqtt_client.disconnect()
        cls.logger.info("end")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_measurement_names(self):
        result = self.influxdb.client.get_list_measurements()
        names = []
        for r in result:
            names.append(r["name"])
        return names

    def test_00ping(self):
        self.logger.info("test_0ping")
        result = self.influxdb.client.ping()
        self.assertIsNotNone(result)

    def test_01database(self):
        self.logger.info("test_1database")
        result = self.influxdb.client.get_list_database()
        self.assertIn({"name":"archippe_test"}, result)

    def test_02create_measurements(self):
        self.logger.info("test_2create_measurements")
        names = self._get_measurement_names()
        for i in range(100000):
            name = "__test_unit__{}".format(i)
            if name not in names:
                break
            name = None
        self.assertIsNotNone(name)
        self.influxdb.write_point(name, 123.456)
        names = self._get_measurement_names()
        self.assertIn(name, names)
        self.influxdb.client.drop_measurement(name)
        names = self._get_measurement_names()
        self.assertNotIn(name, names)

    def test_03create_topic(self):
        self.logger.info("test_3create_topic")
        topic = Topic("/test/topic", "/request/test/topic", "/response/test/topic", float, self.mqtt_client,
                      self.logger, self.influxdb)
        self.assertIsNotNone(topic)
        self.assertEqual(topic._topic_sub, "/test/topic")
        self.assertEqual(self.influxdb.escape_name(topic._topic_sub), "/test/topic")
        self.assertEqual(topic._topic_request, "/request/test/topic")
        self.assertEqual(topic._topic_response, "/response/test/topic")

    def test_04start_stop(self):
        self.logger.info("test_4start_stop")
        topic = Topic("/test/topic", "/request/test/topic", "/response/test/topic", float, self.mqtt_client,
                      self.logger, self.influxdb)
        self.assertNotIn(topic._topic_sub, self.mqtt_client._topic_handler.keys())
        self.assertNotIn(topic._topic_request, self.mqtt_client._topic_handler.keys())
        self.assertNotIn(topic._topic_response, self.mqtt_client._topic_handler.keys())
        topic.start()
        self.assertIn(topic._topic_sub, self.mqtt_client._topic_handler.keys())
        self.assertIn(topic._topic_request, self.mqtt_client._topic_handler.keys())
        self.assertNotIn(topic._topic_response, self.mqtt_client._topic_handler.keys())
        topic.stop()
        self.assertNotIn(topic._topic_sub, self.mqtt_client._topic_handler.keys())
        self.assertNotIn(topic._topic_request, self.mqtt_client._topic_handler.keys())
        self.assertNotIn(topic._topic_response, self.mqtt_client._topic_handler.keys())

    def test_05direct_write(self):
        self.logger.info("test_5direct_write")
        topic = Topic("/test/topic", "/request/test/topic", "/response/test/topic", float, self.mqtt_client,
                      self.logger, self.influxdb)
        value = time.time()
        topic._handler_sub(value)
        time.sleep(0.5)
        self.assertIn(topic._topic_sub, self._get_measurement_names(), "in")
        time.sleep(0.5)
        query = 'select value as value from "{}" ORDER BY time DESC limit 1'.format(topic._topic_sub)
        result = self.influxdb.client.query(query)
        self.assertEqual(value, list(result.get_points())[0]["value"], "equal")

    def test_06float_message(self):
        self.logger.info("test_6direct_read_write")
        event = Event()

        def _handler_response(message):
            msg = message.decode("utf-8")
            message = json.loads(msg)
            self.assertEqual(4, len(message))
            values = []
            for m in message:
                values.append(m["value"])
            self.assertListEqual([2,3,4,5],values)
            event.set()

        topic = Topic("/test/topic", "/request/test/topic", "/response/test/topic", float, self.mqtt_client,
                      self.logger, self.influxdb)
        self.mqtt_client.subscribe(topic._topic_response, _handler_response)

        topic.start()
        time.sleep(1)
        for i in range(0,6):
            self.mqtt_client.publish(topic._topic_sub, float(i))
            time.sleep(0.1)
        topic._handler_request(0.45)
        event.wait()
        topic.stop()
        self.mqtt_client.unsubscribe(topic._topic_response, _handler_response)

    def test_07json_message(self):
        self.logger.info("test_7json_message")
        event = Event()

        def _handler_response(message):
            msg = message.decode("utf-8")
            message = json.loads(msg)
            self.assertEqual(3, len(message))
            values = []
            for m in message:
                values.append(m["value"])
            self.assertListEqual([2,3,4],values)
            event.set()

        topic = Topic("/test/topic", "/request/test/topic", "/response/test/topic", float, self.mqtt_client,
                      self.logger, self.influxdb)
        self.mqtt_client.subscribe(topic._topic_response, _handler_response)

        topic.start()
        time.sleep(1)
        for i in range(0,6):
            self.mqtt_client.publish(topic._topic_sub, float(i))
            time.sleep(0.1)

        f = datetime.datetime.now()-datetime.timedelta(seconds=float(0.45))
        t = datetime.datetime.now() - datetime.timedelta(seconds=float(0.11))
        f = f.strftime(topic._time_format)
        t = t.strftime(topic._time_format)
        j = {"from": f, "to": t}
        self.mqtt_client.publish(topic._topic_request, json.dumps(j))
        event.wait()
        topic.stop()
        self.mqtt_client.unsubscribe(topic._topic_response, _handler_response)

    def test_12json_message_groupby(self):
        self.logger.info("test_12json_message_groupby")
        prog_bar_max = 12
        prog_bar_length = 24
        print("takes apprx. 20s ...")
        printProgressBar(0, prog_bar_max, prefix='Progress:', suffix='Complete', length=prog_bar_length)
        event = Event()

        def _handler_response(message):
            msg = message.decode("utf-8")
            message = json.loads(msg)
            self.assertEqual(3, len(message))
            values = []
            for m in message:
                values.append(m["value"])
            self.assertListEqual([0,1.5,3.5],values)
            event.set()

        topic = Topic("/test/topic", "/request/test/topic", "/response/test/topic", float, self.mqtt_client,
                      self.logger, self.influxdb)
        self.mqtt_client.subscribe(topic._topic_response, _handler_response)

        topic.start()

        # wait until next 10/20/30/40/50/00 second - needed for well defined behavior of group-by
        printProgressBar(1, prog_bar_max, prefix='Progress:', suffix='Complete', length=prog_bar_length)
        c = (10 - time.time() % 10) + 0.5
        self.logger.info("wait {} seconds for next 10/20/30/40/50/00 second - needed for well defined behavior of "
                          "group-by".format(c))
        time.sleep(c)

        printProgressBar(2, prog_bar_max, prefix='Progress:', suffix='Complete', length=prog_bar_length)
        time.sleep(5/2)
        printProgressBar(3, prog_bar_max, prefix='Progress:', suffix='Complete', length=prog_bar_length)
        for i in range(0,6):
            self.mqtt_client.publish(topic._topic_sub, float(i))
            time.sleep(5/2)
            printProgressBar(i+4, prog_bar_max, prefix='Progress:', suffix='Complete', length=prog_bar_length)

        n = datetime.datetime.now()
        f = n - datetime.timedelta(seconds=33/2)
        t = n - datetime.timedelta(seconds=7/2)
        f = f.strftime(topic._time_format)
        t = t.strftime(topic._time_format)
        j = {"from": f, "to": t, "group-by": 10/2}
        self.mqtt_client.publish(topic._topic_request, json.dumps(j))
        printProgressBar(10, prog_bar_max, prefix='Progress:', suffix='Complete', length=prog_bar_length)
        event.wait()
        printProgressBar(11, prog_bar_max, prefix='Progress:', suffix='Complete', length=prog_bar_length)
        topic.stop()
        self.mqtt_client.unsubscribe(topic._topic_response, _handler_response)
        printProgressBar(12, prog_bar_max, prefix='Progress:', suffix='Complete', length=prog_bar_length)

    def test_08write_float(self):
        self.logger.info("test_8write_float")
        topic = Topic("/test/topic/float", "/request/test/topic", "/response/test/topic", float, self.mqtt_client,
                      self.logger, self.influxdb)
        topic._handler_sub(float(1.1))
        topic._handler_sub(int(1))
        topic._handler_sub(bool(True))
        self.assertRaises(ValueError, topic._handler_sub, str("Text"))

    def test_09write_int(self):
        self.logger.info("test_09write_int")
        topic = Topic("/test/topic/int", "/request/test/topic", "/response/test/topic", int, self.mqtt_client,
                      self.logger, self.influxdb)
        topic._handler_sub(float(1.1))
        topic._handler_sub(int(1))
        topic._handler_sub(bool(True))
        self.assertRaises(ValueError, topic._handler_sub, str("Text"))

    def test_10write_bool(self):
        self.logger.info("test_10write_bool")
        topic = Topic("/test/topic/bool", "/request/test/topic", "/response/test/topic", bool, self.mqtt_client,
                      self.logger, self.influxdb)
        topic._handler_sub(float(1.1))
        topic._handler_sub(int(1))
        topic._handler_sub(bool(True))
        topic._handler_sub(str("Text"))

    def test_11write_str(self):
        self.logger.info("test_11write_str")
        topic = Topic("/test/topic/string", "/request/test/topic", "/response/test/topic", str, self.mqtt_client,
                      self.logger, self.influxdb)
        topic._handler_sub(float(1.1))
        topic._handler_sub(int(1))
        topic._handler_sub(bool(True))
        topic._handler_sub(str("Text"))


if __name__ == '__main__':
    unittest.main()
