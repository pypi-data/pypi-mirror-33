import paho.mqtt.client as mqtt
from threading import Event, Lock
import time
from pelops import mylogger


class MQTTClient(object):
    """Wrapper for the paho.mqtt.client. Used by ADriver and DeviceManager but can also be used for other purposes."""

    client = None  # holds an instance of paho.mqtt.client.Client
    _config = None  # json configuration
    _logger = None
    _quiet = None # surpress printing high-level runtime information if set to yes.
    is_connected = None  # threading.Event - True if connection to mqtt broker has been successfully established.
    is_disconnected = None
    _topic_handler = None
    _lock_client = None

    def __init__(self, config, logger, quiet=False):
        self._config = config
        self._logger = mylogger.get_child(logger, __name__, config)
        self._quiet = quiet
        self._logger.info("MQTTClient.__init__ - initalizing")
        self._logger.debug("MQTTClient.__init__ - config: {}.".format(self._config))
        self.is_connected = Event()
        self.is_connected.clear()
        self.is_disconnected = Event()
        self.is_disconnected.set()
        self.client = mqtt.Client()
        self._topic_handler = {}
        self._lock_client = Lock()

    def connect(self):
        """Connect to the mqtt broker using the provided configuration and on_message function."""
        if not self._quiet:
            print("MQTTClient.connect() - Connecting to mqtt.")
        self._logger.info("MQTTClient.connect() - Connecting to mqtt.")
        with self._lock_client:
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.username_pw_set(self._config["mqtt-user"], password=self._config["mqtt-password"])
            self.client.connect(self._config["mqtt-address"], self._config["mqtt-port"], 60)
            self.client.loop_start()
            if self.is_connected.wait(30):
                for topic in self._topic_handler.keys():
                    self._logger.info("MQTTClient.connect() - subscribe to topic '{}'.".format(topic))
                    self.client.subscribe(topic)
            else:
                self._logger.error("MQTTClient.connect - connection to broker could not be established.")
                raise RuntimeError("MQTTClient.connect - connection to broker could not be established.")

    def disconnect(self):
        """Disconnect from mqtt broker and set is_connected to False."""
        with self._lock_client:
            self.client.disconnect()
            self.is_connected.clear()
            self.is_disconnected.set()
        if not self._quiet:
            print("MQTTClient.disconnected()")

    def _on_connect(self, client, userdata, flags, rc):
        """Return code after trying to connect to mqtt brokder. If successfully connected, is_connected is True."""
        if not self._quiet:
            print("MQTTClient._on_connect - Connected with result code " + str(rc))
        self._logger.info("MQTTClient._on_connect - Connected with result code " + str(rc))
        if rc == 0:
            self.is_connected.set()
            self.is_disconnected.clear()

    def _on_message(self, client, userdata, msg):
        t = time.time()

        self._logger.info("MQTTClient._on_message - received message '{}' on topic '{}' @{}s.".
                  format(msg.payload, msg.topic, t))

        for handler in self._topic_handler[msg.topic]:
            self._logger.info("MQTTClient._on_message - calling handler '{}' ({}).".format(handler, t))
            handler(msg.payload)

    def publish(self, topic, msg):
        self._logger.info("MQTTClient.publish - publishing to topic '{}' the message '{}'.".format(topic, msg))
        if self.is_connected.is_set():
            self.client.publish(topic, msg)
        else:
            self._logger.warning("MQTTClient.publish - trying to publish while not being connected to mqtt broker.")
            raise RuntimeWarning("MQTTClient.publish - trying to publish while not being connected to mqtt broker.")

    def subscribe(self, topic, handler):
        self._logger.info("MQTTClient.subscribe - subscribing topic '{}' with handler '{}'.".format(topic, handler))
        with self._lock_client:
            try:
                h = self._topic_handler[topic]
                h.append(handler)
                if h.count(handler) > 1:
                    self._logger.error("MQTTClient.subscribe - topic/handler pair already added. ({}/{})".
                                     format(topic, handler))
                    raise ValueError("MQTTClient.subscribe - topic/handler pair already added. ({}/{})".
                                     format(topic, handler))
            except KeyError:
                self._topic_handler[topic] = [handler,]
            if self.is_connected.is_set():
                self._logger.info("MQTTClient.subscribe - activating topic subscription.")
                self.client.subscribe(topic)

    def unsubscribe(self, topic, handler):
        self._logger.info("MQTTClient.unsubscribe - unsubscribing topic '{}' with handler '{}'.".
                          format(topic, handler))
        with self._lock_client:
            if len(self._topic_handler[topic]) > 1:
                self._topic_handler[topic].remove(handler)
            else:
                del(self._topic_handler[topic])
                self.client.unsubscribe(topic)

    @staticmethod
    def merge(driver, mqtt_client):
        """Utility method - joins a driver instance with an external mqtt-client. Must be called before connecting."""
        driver._mqtt = mqtt_client
        mqtt_client.on_message = driver._on_message
