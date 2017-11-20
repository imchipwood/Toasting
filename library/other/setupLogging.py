import logging


def getLogger(moduleName, DEBUG_LEVEL):

	logger = logging.getLogger(moduleName)
	streamHandler = logging.StreamHandler()
	streamHandler.setLevel(DEBUG_LEVEL)

	stdoutFormat = "%(name)s:%(levelname)s - %(message)s"
	stdoutFormatter = logging.Formatter(stdoutFormat)
	streamHandler.setFormatter(stdoutFormatter)
	logger.addHandler(streamHandler)
	logger.setLevel(DEBUG_LEVEL)

	return logger
