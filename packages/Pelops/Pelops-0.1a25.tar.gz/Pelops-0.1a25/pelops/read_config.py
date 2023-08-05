from pathlib import Path
from pelops import mypyyaml
import os
import jsonschema


def read_config(config_filename='config.yaml'):
    config_file = Path(config_filename)
    if not config_file.is_file():
        raise FileNotFoundError("config file '{}' not found.".format(config_filename))

    with open(config_filename, 'r') as f:
        config = mypyyaml.load(f, Loader=mypyyaml.Loader)

    try:
        with open(os.path.expanduser(config["mqtt"]["mqtt-credentials"]), 'r') as f:
            credentials_mqtt = mypyyaml.load(f, Loader=mypyyaml.Loader)
    except KeyError:
        pass
    else:
        config["mqtt"].update(credentials_mqtt["mqtt"])

    try:
        with open(os.path.expanduser(config["influx"]["influx-credentials"]), 'r') as f:
            credentials_influx = mypyyaml.load(f, Loader=mypyyaml.Loader)
    except KeyError:
        pass
    else:
        config["influx"].update(credentials_influx["influx"])

    config = mypyyaml.dict_deepcopy_lowercase(config)
    return config


def validate_config(config, sub_schema):
    schema = {
                "$schema": "http://json-schema.org/draft-06/schema#",
                "title": "Configuration for pelops mqtt microservice alcathous.",
                "type": "object",
                "properties": {
                    "mqtt": {
                        "description": "Mqtt_client configuration",
                        "type": "object",
                        "properties": {
                            "mqtt-address": {
                                "description": "URL of mqtt broker",
                                "type": "string"
                            },
                            "mqtt-port": {
                                "description": "Port of mqtt broker",
                                "type": "integer",
                                "minimum": 0,
                                "exclusiveMinimum": True
                            },
                            "log-level": {
                                "description": "Log level to be used (optional).",
                                "type": "string",
                                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                            },
                            "mqtt-credentials": {
                                "description": "File containing the credentials (optional).",
                                "type": "string"
                            },
                            "mqtt-user": {
                                "description": "User name for mqtt broker (optional).",
                                "type": "string"
                            },
                            "mqtt-password": {
                                "description": "Password for mqtt broker (optional).",
                                "type": "string"
                            }
                        },
                        "required": ["mqtt-address", "mqtt-port"]
                    },
                    "influx": {
                        "description": "Influx configuration",
                        "type": "object",
                        "properties": {
                            "influx-address": {
                                "description": "URL of influx db",
                                "type": "string"
                            },
                            "influx-port": {
                                "description": "Port of influx db",
                                "type": "integer",
                                "minimum": 0,
                                "exclusiveMinimum": True
                            },
                            "log-level": {
                                "description": "Log level to be used (optional).",
                                "type": "string",
                                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                            },
                            "influx-credentials": {
                                "description": "File containing the credentials (optional).",
                                "type": "string"
                            },
                            "influx-user": {
                                "description": "User name for influx db (optional).",
                                "type": "string"
                            },
                            "influx-password": {
                                "description": "Password for influx db (optional).",
                                "type": "string"
                            },
                            "database": {
                                "description": "Database",
                                "type": "string"
                            }
                        },
                        "required": ["influx-address", "influx-port", "database"]
                    },
                    "logger": {
                        "description": "Logger configuration",
                        "type": "object",
                        "properties": {
                            "log-level": {
                                "description": "Log level to be used.",
                                "type": "string",
                                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                            },
                            "log-file": {
                                "description": "File name for the logger.",
                                "type": "string"
                            }
                        },
                        "required": ["log-level", "log-file"]
                    },
                },
                "required": ["mqtt", "logger"]
             }
    schema["properties"] = {**schema["properties"], **sub_schema}
    for k in sub_schema.keys():
        schema["required"].append(k)

    return jsonschema.validate(config, schema)

