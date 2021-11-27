import re
import logging

global loggers
loggers = dict()


def get_logger(module_name: str, logging_level: int) -> logging.Logger:
    """
    Get a logger object
    @param module_name: name of the module doing the logging
    @param logging_level: what level to log
    @return: logger object
    """
    global loggers
    if str(module_name) in loggers:
        return loggers[str(module_name)]

    # get a fresh logger
    logger = logging.getLogger(str(module_name))
    [logger.removeHandler(handler) for handler in logger.handlers]

    # set up output formatting
    stdout_format = "%(name)s:%(levelname)s - %(message)s"
    stdout_formatter = logging.Formatter(stdout_format)

    # set up stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging_level)
    stream_handler.setFormatter(stdout_formatter)

    # add handler
    logger.addHandler(stream_handler)
    logger.setLevel(logging_level)

    logger.propagate = False

    loggers[str(module_name)] = logger
    return logger


def get_class_name(klass: str or type) -> str:
    """
    Get the name of a class or file
    @param klass: result of __name__ or __class__
    @return: name of class or file
    """
    match = re.search(r"'__\w+__\.(.+)'>", str(klass))
    return match.group(1) if match else None
