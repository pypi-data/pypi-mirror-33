from pelops import mypyyaml
from pelops import mylogger
from pelops import read_config
from pelops.mqttclient import MQTTClient
import argparse
import threading


class AbstractMicroservice:
    _config = None
    _is_stopped = None
    _stop_service = None
    _mqtt_client = None
    _logger = None

    def __init__(self, config, config_class_root_node_name, mqtt_client=None, logger=None, logger_name=None):
        self._config = config[config_class_root_node_name]

        if logger_name is None:
            logger_name = __name__

        if logger is None:
            self._logger = mylogger.create_logger(config["logger"], logger_name)
        else:
            self._logger = logger.getChild(logger_name)

        self._logger.info("{}.__init__ - initializing".format(self.__class__.__name__))
        self._logger.debug("{}.__init__ - config: {}".format(self.__class__.__name__, self._config))

        self._is_stopped = threading.Event()
        self._is_stopped.set()

        self._stop_service = threading.Event()
        self._stop_service.clear()

        if mqtt_client is None:
            self._mqtt_client = MQTTClient(config["mqtt"], self._logger)
        else:
            self._mqtt_client = mqtt_client

        self._logger.info("{}.__init__ - AbstractMicroservice done".format(self.__class__.__name__))

    def _start(self):
        self._logger.warning("{}._start - NotImplementedError".format(self.__class__.__name__))
        raise NotImplementedError

    def start(self):
        print("{} - starting".format(self.__class__.__name__))
        self._logger.info("{} - starting".format(self.__class__.__name__))
        self._is_stopped.clear()
        self._mqtt_client.connect()
        self._mqtt_client.is_connected.wait()
        self._start()
        self._stop_service.clear()
        self._logger.info("{} - started".format(self.__class__.__name__))

    def _stop(self):
        self._logger.warning("{}._stop - NotImplementedError".format(self.__class__.__name__))
        raise NotImplementedError

    def stop(self):
        self._logger.info("{} - stopping".format(self.__class__.__name__))
        self._stop_service.set()
        self._stop()
        self._is_stopped.set()
        print("{} - stopped".format(self.__class__.__name__))
        self._logger.info("{} - stopped".format(self.__class__.__name__))

    @classmethod
    def _get_schema(cls):
        raise NotImplementedError

    @classmethod
    def _get_description(cls):
        raise NotImplementedError

    @classmethod
    def _args_to_config(cls, args=None):
        """Handle command line arguments and read the yaml file into a json structure (=config)."""
        desc = cls._get_description()
        ap = argparse.ArgumentParser(description=desc)
        ap.add_argument('-c', '--config', type=str, help='yaml config file', required=True)
        ap.add_argument('--version', action='version',
                            version='%(prog)s {}'.format(cls._version),
                            help='show the version number and exit')
        if args:
            arguments = vars(ap.parse_args(args))
        else:
            arguments = vars(ap.parse_args())

        config_filename = arguments["config"]
        config = read_config.read_config(config_filename)

        return config

    @classmethod
    def standalone(cls, args=None):
        """Public method to start this driver directly. Instantiates an MQTT client and creates an object for the
                given driver."""
        config = cls._args_to_config(args)
        config = mypyyaml.dict_deepcopy_lowercase(config)

        validation_result = read_config.validate_config(config, cls._get_schema())
        if validation_result:
            raise ValueError("Validation of config file failed: {}".format(validation_result))

        instance = None

        try:
            instance = cls(config)
            instance.start()

            try:
                while not instance._is_stopped.wait(0.1):  # timeout is necessary for CTRL+C
                    pass
            except KeyboardInterrupt:
                instance._logger.info("KeyboardInterrupt")
                pass

            instance.stop()
        except Exception as e:
            if instance is not None and instance._logger is not None:
                instance._logger.error(e)
            raise

