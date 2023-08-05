import logging


def _get_log_level(level):
    if level.upper() == "CRITICAL":
        level = logging.CRITICAL
    elif level.upper() == "ERROR":
        level = logging.ERROR
    elif level.upper() == "WARNING":
        level = logging.WARNING
    elif level.upper() == "INFO":
        level = logging.INFO
    elif level.upper() == "DEBUG":
        level = logging.DEBUG
    else:
        raise ValueError("unknown value for logger level ('{}').".format(level))
    return level


def get_child(logger, package_name, config=None):
    child = logger.getChild(package_name)
    if config is not None:
        try:
            log_level = config["log-level"]
            level = _get_log_level(log_level)
            child.setLevel(level)
        except KeyError:
            pass
    return child


def create_logger(config, package_name):
    log_level = config["log-level"]
    level = _get_log_level(log_level)

    logger = logging.getLogger(package_name)
    logger.setLevel(level)

    if not len(logger.handlers):
        handler = logging.FileHandler(config["log-file"])
        handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
