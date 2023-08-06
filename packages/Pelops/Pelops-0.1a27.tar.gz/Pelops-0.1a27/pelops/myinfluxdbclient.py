from influxdb import InfluxDBClient
from pelops.mylogger import get_child
import datetime


class MyInfluxDBClient:
    client = None
    _influxdb_username = None
    _influxdb_password = None
    _influxdb_address = None
    _influxdb_port = None
    _influxdb_database = None

    _config = None
    _logger = None

    def __init__(self, config, logger):
        self._config = config
        self._logger = get_child(logger, __name__, config)
        self._logger.info("MyInfluxDBClient.__init__ - creating instance.")
        self._logger.debug("MyInfluxDBClient.__init__ - config: {}".format(self._config))

        self._influxdb_address = str(self._config["influx-address"])
        self._influxdb_port = int(self._config["influx-port"])
        self._influxdb_database = str(self._config["database"])
        self._influxdb_password = str(self._config["influx-password"])
        self._influxdb_username = str(self._config["influx-user"])

        self.client = InfluxDBClient(host=self._influxdb_address, port=self._influxdb_port,
                                     username=self._influxdb_username, password=self._influxdb_password,
                                     database=self._influxdb_database)

    def write_point(self, measurement, value, timestamp = None):
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")  # "2009-11-10T23:00:00.0Z"
        json_body = [
            {
                "measurement": MyInfluxDBClient.escape_name(measurement),
                "tags": {},
                "time": timestamp,
                "fields": {
                    "value": value
                }
            }
        ]
        self._logger.info("Write a point: (measurement: {}, timestamp: {}, value: {})".
                          format(measurement, timestamp, value))
        self._logger.debug("Json: {}.".format(json_body))
        self.client.write_points(json_body)

    @staticmethod
    def escape_name(name):
        # https://stackoverflow.com/questions/47273602/how-to-insert-store-a-string-value-in-influxdb-measurement
        name = name.replace(" ", "\ ")
        name = name.replace(",", "\,")
        return name
